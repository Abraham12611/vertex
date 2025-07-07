from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.base import SessionLocal
from db.models.user import User
from core.security import hash_password, verify_password, create_access_token
from sqlalchemy.future import select

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterRequest):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == data.email))
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = User(email=data.email, hashed_password=hash_password(data.password))
        session.add(new_user)
        await session.commit()
        return {"msg": "registered"}

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(data: LoginRequest):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == data.email))
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
