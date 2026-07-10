import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from studysherpa.core.config import settings


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    hash_bytes = hashed_password.encode("utf-8")
    plain_bytes = plain_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hash_bytes)


def create_jwt_token(
    user_id: int,
    expires_delta: timedelta = timedelta(minutes=settings.jwt_expires_minutes),
) -> str:
    exp = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": str(user_id), "exp": exp}
    return jwt.encode(payload, settings.jwt_secret_key, settings.jwt_algorithm)


def verify_jwt_token(token: str) -> int:
    payload = jwt.decode(
        token, key=settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    return int(payload["sub"])


def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
