import bcrypt

def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_passowrd: str):
    hash_bytes = hashed_passowrd.encode('utf-8')
    plain_bytes = plain_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hash_bytes)

