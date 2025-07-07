from argon2 import PasswordHasher
from jose import jwt
from datetime import datetime, timedelta
from core.settings import settings

ph = PasswordHasher()
JWT_SECRET = settings.JWT_SECRET

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return ph.verify(hashed, password)

def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
