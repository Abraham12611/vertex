from argon2 import PasswordHasher
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from core.settings import settings

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        return ph.verify(hashed, password)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: int = 3600) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def create_user_token(user_id: int, email: str, expires_delta: int = 3600) -> str:
    """Create a JWT token for a user"""
    data = {
        "sub": str(user_id),
        "email": email,
        "type": "access"
    }
    return create_access_token(data, expires_delta)

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Extract user information from a JWT token"""
    payload = verify_token(token)
    if payload and payload.get("type") == "access":
        return {
            "user_id": int(payload["sub"]),
            "email": payload["email"]
        }
    return None
