from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.core.security import hash_refresh_token, verify_jwt_token
from studysherpa.db import RefreshToken


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert login.status_code == 200
    token_before_refresh = client.cookies.get("refresh_token")
    assert token_before_refresh is not None
    response = await client.post("/api/refresh")
    assert response.status_code == 200
    data = response.json()
    token_after_refresh = client.cookies.get("refresh_token")
    assert token_after_refresh is not None

    assert verify_jwt_token(data["access_token"]) == register.json()["id"]
    assert data["token_type"] == "bearer"
    assert token_after_refresh != token_before_refresh


@pytest.mark.asyncio
async def test_refresh_expired_token(client: AsyncClient, db_session: AsyncSession):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert login.status_code == 200
    raw_token = client.cookies.get("refresh_token")
    assert raw_token is not None
    stored_token = await db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(raw_token)
        )
    )
    assert stored_token is not None
    stored_token.expires_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    await db_session.commit()
    response = await client.post("/api/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_revoked_token(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    old_refresh_token = client.cookies.get("refresh_token")
    assert old_refresh_token is not None
    first_refresh = await client.post("/api/refresh")
    assert first_refresh.status_code == 200
    client.cookies.set("refresh_token", old_refresh_token)
    reused_refresh = await client.post("/api/refresh")
    assert reused_refresh.status_code == 401


@pytest.mark.asyncio
async def test_refresh_nonexistent_token(client: AsyncClient):
    response = await client.post("/api/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rate_limiter(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201
    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    refresh_token = client.cookies.get("refresh_token")
    assert refresh_token is not None
    for _ in range(20):
        response = await client.post(
            "/api/refresh",
        )
        assert response.status_code == 200
        refresh_token = client.cookies.get("refresh_token")
        assert refresh_token is not None
    refresh_limit_reached = await client.post(
        "/api/refresh",
    )
    assert refresh_limit_reached.status_code == 429
