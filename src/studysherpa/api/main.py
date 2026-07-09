from fastapi import Depends, FastAPI, HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.api.schemas import Token, UserCreate, UserLogin, UserPublic
from studysherpa.core.config import settings
from studysherpa.core.database import get_db
from studysherpa.core.security import create_jwt_token, hash_password, verify_password
from studysherpa.db import User

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="StudySherpa")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
@limiter.limit(limit_value=settings.register_rate_limit)
async def register(
    request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> User:
    existing = await db.scalar(select(User).where(User.email == user_data.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    user = User(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Race condition"
        )
    await db.refresh(user)

    return user


@app.post("/login", response_model=Token)
@limiter.limit(limit_value=settings.login_rate_limit)
async def login(
    request: Request, credentials: UserLogin, db: AsyncSession = Depends(get_db)
) -> Token:
    user = await db.scalar(select(User).where(User.email == credentials.email))
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    jwt_token = create_jwt_token(user.id)
    token = Token(access_token=jwt_token, token_type="bearer")
    return token
