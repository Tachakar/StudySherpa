from studysherpa.core.security import hash_password, verify_password


def test_hash_password_produces_bcrypt_hash():
    hashed = hash_password("password")

    assert hashed.startswith("$2b$")
    assert hashed != "password"


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
