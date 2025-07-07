from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID

from db.base import SessionLocal
from db.models.user import User
from db.models.organization import Organization
from db.models.user_organization import UserOrganization
from core.security import hash_password, verify_password, create_access_token, get_password_hash
from core.settings import settings
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models for request/response
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    organization_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    organizations: list = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """Register a new user and optionally create an organization."""
    async with SessionLocal() as session:
        # Check if user already exists
        existing_user = await session.scalar(
            select(User).where(User.email == data.email)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(data.password)
        new_user = User(
            email=data.email,
            hashed_password=hashed_password
        )
        session.add(new_user)
        await session.flush()  # Get the user ID

        # Create organization if provided
        if data.organization_name:
            organization = Organization(name=data.organization_name)
            session.add(organization)
            await session.flush()

            # Link user to organization
            user_org = UserOrganization(
                user_id=new_user.id,
                organization_id=organization.id
            )
            session.add(user_org)

        await session.commit()

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id)}, expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                created_at=new_user.created_at,
                organizations=[]
            )
        )

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """Authenticate user and return access token."""
    async with SessionLocal() as session:
        user = await session.scalar(
            select(User).where(User.email == data.email)
        )

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        # Get user's organizations
        user_with_orgs = await session.execute(
            select(User)
            .options(selectinload(User.organizations))
            .where(User.id == user.id)
        )
        user = user_with_orgs.scalar_one()

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
                organizations=[org.name for org in user.organizations]
            )
        )

@router.post("/login/form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login."""
    async with SessionLocal() as session:
        user = await session.scalar(
            select(User).where(User.email == form_data.username)
        )

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

@router.post("/password-reset")
async def request_password_reset(data: PasswordResetRequest):
    """Request password reset (sends email in production)."""
    async with SessionLocal() as session:
        user = await session.scalar(
            select(User).where(User.email == data.email)
        )

        if user:
            # In production, send email with reset token
            # For demo, just return success
            return {"message": "If email exists, password reset instructions sent"}

        # Don't reveal if email exists or not
        return {"message": "If email exists, password reset instructions sent"}

@router.post("/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm):
    """Confirm password reset with token."""
    # In production, verify token and update password
    # For demo, just return success
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        organizations=[]
    )

@router.post("/logout")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Successfully logged out"}
