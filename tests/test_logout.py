import pytest
from httpx import AsyncClient

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studysherpa.core.security import hash_refresh_token
from studysherpa.db import RefreshToken


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, db_session: AsyncSession):
    register = await client.post(
        "/register", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/login", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert login.status_code == 200

    refresh_token = login.json()["refresh_token"]

    logout = await client.post("/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 204

    stored_token = await db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(refresh_token)
        )
    )

    assert stored_token is not None
    assert stored_token.revoked_at is not None

    refresh_attempt = await client.post(
        "/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_attempt.status_code == 401


@pytest.mark.asyncio
async def test_logout_noneexistant_token(client: AsyncClient):
    response = await client.post("/logout", json={"refresh_token": "noneexistant"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_already_revoked_token(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/login", json={"email": "test@exmaple.com", "password": "strongpassword"}
    )
    assert login.status_code == 200

    refresh_token = login.json()["refresh_token"]

    first_logout = await client.post("/logout", json={"refresh_token": refresh_token})
    assert first_logout.status_code == 204
    second_logout = await client.post("/logout", json={"refresh_token": refresh_token})
    assert second_logout.status_code == 401
