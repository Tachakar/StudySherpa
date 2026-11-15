from argon2 import PasswordHasher

from studysherpa.core.security import (
    hash_password,
    password_needs_rehash,
    verify_password,
)


def test_hash_password_produces_argon2id_hash():
    hashed = hash_password("password")

    assert hashed.startswith("$argon2id$")
    assert "password" not in hashed


def test_verify_password_correct():
    hashed = hash_password("password")

    assert verify_password("password", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("password")

    assert verify_password("wrong_password", hashed) is False


def test_same_password_produces_different_hashes():
    hash_a = hash_password("password")
    hash_b = hash_password("password")

    assert hash_a != hash_b


def test_password_longer_than_72_bytes():
    long_password = "ą" * 100
    hashed = hash_password(long_password)

    assert verify_password(long_password, hashed) is True
    assert verify_password(long_password[:-1], hashed) is False


def test_current_hash_does_not_need_rehash():
    assert password_needs_rehash(hash_password("password")) is False


def test_weaker_hash_needs_rehash():
    weak_hasher = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)

    assert password_needs_rehash(weak_hasher.hash("password")) is True
