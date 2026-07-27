from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.api.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserPublic,
)
from studysherpa.core.config import settings
from studysherpa.core.database import get_db
from studysherpa.core.security import (
    create_jwt_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from studysherpa.db import RefreshToken, User

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api")
app = FastAPI(title="StudySherpa")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = settings.cors_allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
@limiter.limit(limit_value=settings.register_rate_limit)
async def register(
    request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)
):
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


@router.post("/login", response_model=Token)
@limiter.limit(limit_value=settings.login_rate_limit)
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await db.scalar(select(User).where(User.email == credentials.email))
    found_hash = user.hashed_password if user is not None else None
    if found_hash is not None:
        password_ok = verify_password(credentials.password, found_hash)
    else:
        password_ok = verify_password(credentials.password)
    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    jwt_token = create_jwt_token(user.id)
    raw_refresh_token = create_refresh_token()
    refresh_token_db = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=datetime.now(tz=timezone.utc)
        + timedelta(days=settings.refresh_token_expires_days),
    )
    db.add(refresh_token_db)
    await db.commit()
    response.set_cookie(
        "refresh_token",
        raw_refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expires_days * 86400,
        secure=True if settings.cookie_secure else False,
        samesite="strict",
    )
    token = Token(access_token=jwt_token, token_type="bearer")
    return token


@router.post("/refresh", response_model=Token)
@limiter.limit(limit_value=settings.refresh_rate_limit)
async def refresh(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
) -> Token:
    raw_refresh_token = request.cookies.get("refresh_token")
    if raw_refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    token_hash = hash_refresh_token(raw_refresh_token)
    stored_token = await db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )
    if stored_token is None or stored_token.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    if stored_token.revoked_at is not None:
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == stored_token.user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(tz=timezone.utc))
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    stored_token.revoked_at = datetime.now(tz=timezone.utc)
    new_raw_refresh_token = create_refresh_token()
    hashed_refreshed_token = RefreshToken(
        user_id=stored_token.user_id,
        token_hash=hash_refresh_token(new_raw_refresh_token),
        expires_at=datetime.now(tz=timezone.utc)
        + timedelta(days=settings.refresh_token_expires_days),
    )
    db.add(hashed_refreshed_token)
    new_access_token = create_jwt_token(stored_token.user_id)
    await db.commit()
    response.set_cookie(
        "refresh_token",
        new_raw_refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expires_days * 86400,
        secure=True if settings.cookie_secure else False,
        samesite="strict",
    )
    return Token(
        access_token=new_access_token,
        token_type="bearer",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
) -> None:
    token_hash = hash_refresh_token(request.cookies.get("refresh_token", ""))
    stored_token = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    if stored_token is None or stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    stored_token.revoked_at = datetime.now(tz=timezone.utc)
    await db.commit()
    response.delete_cookie("refresh_token")


@router.get("/user", response_model=UserPublic)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


app.include_router(router)
