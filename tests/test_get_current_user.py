from datetime import timedelta

import pytest
from httpx import AsyncClient

from studysherpa.core.security import create_jwt_token


@pytest.mark.asyncio
async def test_user_endpoint_valid(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert login.status_code == 200

    access_token = login.json()["access_token"]
    response = await client.get(
        "/api/user", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["id"] == register.json()["id"]


@pytest.mark.asyncio
async def test_user_endpoint_missing_header(client: AsyncClient):
    response = await client.get("/api/user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_user_endpoint_malformed_token(client: AsyncClient):
    response = await client.get(
        "/api/user", headers={"Authorization": "Bearer not a token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_user_endpoint_expired_token(client: AsyncClient):
    register = await client.post(
        "/api/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    user_id = register.json()["id"]
    token = create_jwt_token(user_id, expires_delta=timedelta(seconds=-1))

    response = await client.get("/api/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_user_endpoint_nonexistent_user(client: AsyncClient):
    token = create_jwt_token(999999)

    response = await client.get("/api/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
