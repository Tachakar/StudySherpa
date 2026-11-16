from http.cookies import SimpleCookie

import pytest
from argon2 import PasswordHasher
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.core.config import settings
from studysherpa.core.security import (
    password_needs_rehash,
    verify_jwt_token,
    verify_password,
)
from studysherpa.db import User


@pytest.mark.asyncio
async def test_login_rehashes_outdated_hash(
    client: AsyncClient, db_session: AsyncSession
):
    weak_hasher = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    user = User(
        email="test@example.com", hashed_password=weak_hasher.hash("strongpassword")
    )
    db_session.add(user)
    await db_session.commit()
    outdated_hash = user.hashed_password

    response = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert response.status_code == 200

    await db_session.refresh(user)
    assert user.hashed_password != outdated_hash
    assert password_needs_rehash(user.hashed_password) is False
    assert verify_password("strongpassword", user.hashed_password) is True


@pytest.mark.asyncio
async def test_login_keeps_current_hash(client: AsyncClient, db_session: AsyncSession):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201
    user = await db_session.get(User, register.json()["id"])
    assert user is not None
    hash_before_login = user.hashed_password

    response = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert response.status_code == 200

    await db_session.refresh(user)
    assert user.hashed_password == hash_before_login


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201
    response = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    data = response.json()
    assert verify_jwt_token(data["access_token"]) == register.json()["id"]
    assert response.status_code == 200
    assert data["token_type"] == "bearer"
    assert "access_token" in data.keys()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201
    response = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_email_and_password_same_msg(client: AsyncClient):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201

    wrong_password = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    nonexistent_user = await client.post(
        "/api/login", json={"email": "nobody@example.com", "password": "wrongpassword"}
    )
    assert wrong_password.json()["detail"] == nonexistent_user.json()["detail"]


@pytest.mark.asyncio
async def test_login_rate_limiter(client: AsyncClient):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201
    for _ in range(5):
        login = await client.post(
            "/api/login",
            json={"email": "test@example.com", "password": "strongpassword"},
        )
        assert login.status_code == 200
    login_limit_reached = await client.post(
        "/api/login",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert login_limit_reached.status_code == 429


@pytest.mark.asyncio
async def test_check_cookies_after_login(client: AsyncClient):
    register = await client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    headers = login.headers.get_list("set-cookie")
    assert len(headers) == 1
    for header in headers:
        cookie = SimpleCookie()
        cookie.load(header)
        assert len(cookie) > 0
        token = cookie.get("refresh_token")
        assert token is not None
        assert int(token["max-age"]) == settings.refresh_token_expires_days * 86400
        assert token["samesite"] == "strict"
        assert token["httponly"] is True
        assert bool(token["secure"]) == (settings.cookie_secure)
