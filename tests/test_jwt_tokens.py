from datetime import timedelta, datetime, timezone

import jwt
import pytest


from studysherpa.core.config import settings
from studysherpa.core.security import verify_jwt_token, create_jwt_token

TEST_KEY = "sadjjl123kasd"


def test_round_trip():
    assert verify_jwt_token(create_jwt_token(1)) == 1


def test_expired_token():
    token = create_jwt_token(1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        _ = verify_jwt_token(token)


def test_wrong_token_signature():
    payload = {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=30.0)}
    token = jwt.encode(payload, key=TEST_KEY, algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.InvalidSignatureError):
        _ = verify_jwt_token(token)


def test_manipulated_token():
    token = create_jwt_token(1)
    token = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(jwt.InvalidSignatureError):
        _ = verify_jwt_token(token)


def test_random_token():
    with pytest.raises(jwt.DecodeError):
        _ = verify_jwt_token("not a token")
