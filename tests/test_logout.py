import pytest
from httpx import AsyncClient

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.core.security import hash_refresh_token
from studysherpa.db import RefreshToken


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, db_session: AsyncSession):
    register = await client.post(
        "/api/register", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert login.status_code == 200
    raw = client.cookies.get("refresh_token")
    assert raw is not None
    logout = await client.post("/api/logout")
    assert logout.status_code == 204
    stored_token = await db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw))
    )

    assert stored_token is not None
    assert stored_token.revoked_at is not None

    refresh_attempt = await client.post("/api/refresh")

    assert refresh_attempt.status_code == 401


@pytest.mark.asyncio
async def test_logout_noneexistant_token(client: AsyncClient):
    response = await client.post("/api/logout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_already_revoked_token(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert login.status_code == 200

    raw = client.cookies.get("refresh_token")
    assert raw is not None

    first_logout = await client.post("/api/logout")
    assert first_logout.status_code == 204
    second_logout = await client.post("/api/logout")
    assert second_logout.status_code == 401
