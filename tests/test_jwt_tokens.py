from datetime import UTC, datetime, timedelta

import jwt
import pytest

from studysherpa.core.config import settings
from studysherpa.core.security import create_jwt_token, verify_jwt_token

TEST_KEY = "sadjjl123kasd"


def test_round_trip():
    assert verify_jwt_token(create_jwt_token(1)) == 1


def test_expired_token():
    token = create_jwt_token(1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        _ = verify_jwt_token(token)


def test_wrong_token_signature():
    payload = {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=30.0)}
    token = jwt.encode(payload, key=TEST_KEY, algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.InvalidSignatureError):
        _ = verify_jwt_token(token)


def test_manipulated_token():
    header, payload, signature = create_jwt_token(1).split(".")
    payload = ("a" if payload[0] != "a" else "b") + payload[1:]
    token = ".".join([header, payload, signature])
    with pytest.raises(jwt.InvalidSignatureError):
        _ = verify_jwt_token(token)


def test_random_token():
    with pytest.raises(jwt.DecodeError):
        _ = verify_jwt_token("not a token")


def test_invalid_sub_raises_error():
    with pytest.raises(jwt.InvalidTokenError):
        verify_jwt_token(
            jwt.encode(
                {
                    "sub": "abc",
                    "exp": datetime.now(UTC) + timedelta(minutes=30.0),
                },
                key=settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm,
            )
        )


def test_token_without_exp_raises_error():
    with pytest.raises(jwt.InvalidTokenError):
        verify_jwt_token(
            jwt.encode(
                {"sub": "1"},
                key=settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm,
            )
        )
