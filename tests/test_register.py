import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user(client: AsyncClient):
    response = await client.post(
        "/register",
        json={"email": "test@example.com", "password": "strongpassword"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient):
    payload = {"email": "duplicate@example.com", "password": "strongpassword"}

    first = await client.post("/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/register", json=payload)
    assert second.status_code == 409
