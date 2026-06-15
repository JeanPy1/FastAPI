
from passlib.context import CryptContext

crypt = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return crypt.hash(password)

def verify_password(password: str, password_hash: str):
    return crypt.verify(password, password_hash)

