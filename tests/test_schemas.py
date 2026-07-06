import pytest
from pydantic import ValidationError

from studysherpa.api.schemas import UserCreate, UserPublic


def test_user_create_accepts_valid_email():
    user = UserCreate(email="test@example.com", password="password")

    assert user.email == "test@example.com"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="wrong_email@@@test.pl", password="password")

def test_user_create_immutability():
    user_create = UserCreate(email="test@example.com", password="password")
    with pytest.raises(ValidationError):
        user_create.email = "test2@example.com"

def test_user_public_immutability():
    user_public = UserPublic(id=1, email="test@example.com")
    with pytest.raises(ValidationError):
        user_public.email = "test2@example.com"
