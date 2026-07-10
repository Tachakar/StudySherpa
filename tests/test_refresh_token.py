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
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/login", json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert login.status_code == 200
    login_data = login.json()
    response = await client.post(
        "/refresh", json={"refresh_token": login_data["refresh_token"]}
    )
    assert response.status_code == 200
    data = response.json()

    assert verify_jwt_token(data["access_token"]) == register.json()["id"]
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != login_data["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_expired_token(client: AsyncClient, db_session: AsyncSession):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/login", json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert login.status_code == 200
    raw_refresh_token = login.json()["refresh_token"]
    stored_token = await db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(raw_refresh_token)
        )
    )
    assert stored_token is not None
    stored_token.expires_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    await db_session.commit()
    response = await client.post("/refresh", json={"refresh_token": raw_refresh_token})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_revoked_token(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    old_refresh_token = login.json()["refresh_token"]

    first_refresh = await client.post(
        "/refresh", json={"refresh_token": old_refresh_token}
    )
    assert first_refresh.status_code == 200

    reused_refresh = await client.post(
        "/refresh", json={"refresh_token": old_refresh_token}
    )
    assert reused_refresh.status_code == 401


@pytest.mark.asyncio
async def test_refresh_nonexistent_token(client: AsyncClient):
    response = await client.post(
        "/refresh", json={"refresh_token": "totally-made-up-token-value"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rate_limiter(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201
    login = await client.post(
        "/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]
    for _ in range(20):
        response = await client.post(
            "/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        refresh_token = response.json()["refresh_token"]
    refresh_limit_reached = await client.post(
        "/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_limit_reached.status_code == 429
