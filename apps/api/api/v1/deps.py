from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import jwt, JWTError
from typing import Optional, List
from uuid import UUID

from db.base import SessionLocal
from db.models.user import User
from db.models.organization import Organization
from db.models.project import Project
from core.settings import settings
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer()

# Token validation and user extraction
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        return user

# Organization and project access control
async def get_user_organizations(user: User = Depends(get_current_user)) -> List[Organization]:
    """Get organizations that the current user belongs to."""
    async with SessionLocal() as session:
        user_with_orgs = await session.execute(
            select(User)
            .options(selectinload(User.organizations))
            .where(User.id == user.id)
        )
        user = user_with_orgs.scalar_one()
        return user.organizations

async def get_user_projects(user: User = Depends(get_current_user)) -> List[Project]:
    """Get projects that the current user has access to."""
    async with SessionLocal() as session:
        # Get user's organizations
        user_with_orgs = await session.execute(
            select(User)
            .options(selectinload(User.organizations))
            .where(User.id == user.id)
        )
        user = user_with_orgs.scalar_one()

        # Get projects from user's organizations
        projects = []
        for org in user.organizations:
            org_projects = await session.execute(
                select(Project).where(Project.organization_id == org.id)
            )
            projects.extend(org_projects.scalars().all())

        return projects

async def verify_project_access(
    project_id: UUID,
    user: User = Depends(get_current_user)
) -> Project:
    """Verify that the user has access to the specified project."""
    async with SessionLocal() as session:
        # Get project with organization
        project = await session.execute(
            select(Project)
            .options(selectinload(Project.organization))
            .where(Project.id == project_id)
        )
        project = project.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check if user belongs to the project's organization
        user_orgs = await session.execute(
            select(User)
            .options(selectinload(User.organizations))
            .where(User.id == user.id)
        )
        user = user_orgs.scalar_one()

        if project.organization not in user.organizations:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to project"
            )

        return project

async def verify_organization_access(
    organization_id: UUID,
    user: User = Depends(get_current_user)
) -> Organization:
    """Verify that the user has access to the specified organization."""
    async with SessionLocal() as session:
        # Check if user belongs to the organization
        user_orgs = await session.execute(
            select(User)
            .options(selectinload(User.organizations))
            .where(User.id == user.id)
        )
        user = user_orgs.scalar_one()

        organization = None
        for org in user.organizations:
            if org.id == organization_id:
                organization = org
                break

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to organization"
            )

        return organization

# Role-based access control (for future use)
async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role for access."""
    # For demo, all users are considered admins
    # In production, you'd check user roles
    return user

async def require_org_admin(
    organization_id: UUID,
    user: User = Depends(get_current_user)
) -> User:
    """Require organization admin role for access."""
    # For demo, all users are considered org admins
    # In production, you'd check user roles within the organization
    return user

# Rate limiting (for future use)
class RateLimiter:
    def __init__(self):
        self.requests = {}

    def is_allowed(self, user_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if user is within rate limits."""
        import time
        now = time.time()

        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < window
        ]

        # Check if under limit
        if len(self.requests[user_id]) >= limit:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()

async def check_rate_limit(
    user: User = Depends(get_current_user),
    limit: int = 100,
    window: int = 3600
) -> User:
    """Check rate limits for the current user."""
    if not rate_limiter.is_allowed(str(user.id), limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    return user

# WebSocket authentication helper
async def get_current_user_ws(websocket) -> Optional[User]:
    """Get current user from WebSocket connection."""
    try:
        # Extract token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            return None

        # Verify token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id:
            async with SessionLocal() as session:
                user = await session.get(User, user_id)
                return user
    except:
        pass
    return None

# Utility functions
def decode_access_token(token: str) -> dict:
    """Decode JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def create_access_token(data: dict, expires_delta=None) -> str:
    """Create JWT access token."""
    from datetime import datetime, timedelta

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt
