import pytest
from httpx import AsyncClient

from studysherpa.core.security import verify_jwt_token


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201
    response = await client.post(
        "/login", json={"email": "test@example.com", "password": "strongpassword"}
    )
    data = response.json()
    assert verify_jwt_token(data["access_token"]) == register.json()["id"]
    assert response.status_code == 200
    assert data["token_type"] == "bearer"
    assert "access_token" in data.keys()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201
    response = await client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_email_and_password_same_msg(client: AsyncClient):
    register = await client.post(
        "/register", json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert register.status_code == 201

    wrong_password = await client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    nonexistent_user = await client.post(
        "/login", json={"email": "nobody@example.com", "password": "wrongpassword"}
    )
    assert wrong_password.json()["detail"] == nonexistent_user.json()["detail"]
