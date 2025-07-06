from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.prompt import Prompt
from db.models.project import Project
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models
class PromptCategory(str, Enum):
    strategy = "strategy"
    content = "content"
    community = "community"
    analytics = "analytics"
    general = "general"

class PromptType(str, Enum):
    template = "template"
    custom = "custom"
    system = "system"

class PromptCreate(BaseModel):
    project_id: UUID
    title: str
    content: str
    category: PromptCategory
    prompt_type: PromptType = PromptType.custom
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: bool = False

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[PromptCategory] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

class PromptResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    content: str
    category: PromptCategory
    prompt_type: PromptType
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    avg_rating: Optional[float] = None

class PromptAnalytics(BaseModel):
    total_prompts: int
    prompts_by_category: Dict[str, int]
    most_used_prompts: List[PromptResponse]
    avg_usage_per_prompt: float

# Prompt CRUD operations
@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new prompt."""
    async with SessionLocal() as session:
        # Verify project exists
        project = await session.get(Project, prompt_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        prompt = Prompt(
            project_id=prompt_data.project_id,
            title=prompt_data.title,
            content=prompt_data.content,
            category=prompt_data.category,
            prompt_type=prompt_data.prompt_type,
            tags=prompt_data.tags or [],
            metadata=prompt_data.metadata or {},
            is_public=prompt_data.is_public
        )

        session.add(prompt)
        await session.commit()
        await session.refresh(prompt)

        return PromptResponse(
            id=prompt.id,
            project_id=prompt.project_id,
            title=prompt.title,
            content=prompt.content,
            category=prompt.category,
            prompt_type=prompt.prompt_type,
            tags=prompt.tags or [],
            metadata=prompt.metadata or {},
            is_public=prompt.is_public,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            usage_count=0,
            avg_rating=None
        )

@router.get("/", response_model=List[PromptResponse])
async def list_prompts(
    project_id: Optional[UUID] = None,
    category: Optional[PromptCategory] = None,
    prompt_type: Optional[PromptType] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """List prompts with optional filters."""
    async with SessionLocal() as session:
        query = select(Prompt)

        if project_id:
            query = query.where(Prompt.project_id == project_id)
        if category:
            query = query.where(Prompt.category == category)
        if prompt_type:
            query = query.where(Prompt.prompt_type == prompt_type)
        if is_public is not None:
            query = query.where(Prompt.is_public == is_public)
        if search:
            query = query.where(
                (Prompt.title.ilike(f"%{search}%")) |
                (Prompt.content.ilike(f"%{search}%"))
            )

        query = query.order_by(Prompt.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        prompts = result.scalars().all()

        return [
            PromptResponse(
                id=prompt.id,
                project_id=prompt.project_id,
                title=prompt.title,
                content=prompt.content,
                category=prompt.category,
                prompt_type=prompt.prompt_type,
                tags=prompt.tags or [],
                metadata=prompt.metadata or {},
                is_public=prompt.is_public,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at,
                usage_count=0,  # Would need to track usage
                avg_rating=None
            )
            for prompt in prompts
        ]

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get specific prompt by ID."""
    async with SessionLocal() as session:
        prompt = await session.get(Prompt, prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )

        return PromptResponse(
            id=prompt.id,
            project_id=prompt.project_id,
            title=prompt.title,
            content=prompt.content,
            category=prompt.category,
            prompt_type=prompt.prompt_type,
            tags=prompt.tags or [],
            metadata=prompt.metadata or {},
            is_public=prompt.is_public,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            usage_count=0,
            avg_rating=None
        )

@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_data: PromptUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update prompt."""
    async with SessionLocal() as session:
        prompt = await session.get(Prompt, prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )

        if prompt_data.title is not None:
            prompt.title = prompt_data.title
        if prompt_data.content is not None:
            prompt.content = prompt_data.content
        if prompt_data.category is not None:
            prompt.category = prompt_data.category
        if prompt_data.tags is not None:
            prompt.tags = prompt_data.tags
        if prompt_data.metadata is not None:
            prompt.metadata = prompt_data.metadata
        if prompt_data.is_public is not None:
            prompt.is_public = prompt_data.is_public

        await session.commit()
        await session.refresh(prompt)

        return PromptResponse(
            id=prompt.id,
            project_id=prompt.project_id,
            title=prompt.title,
            content=prompt.content,
            category=prompt.category,
            prompt_type=prompt.prompt_type,
            tags=prompt.tags or [],
            metadata=prompt.metadata or {},
            is_public=prompt.is_public,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            usage_count=0,
            avg_rating=None
        )

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete prompt."""
    async with SessionLocal() as session:
        prompt = await session.get(Prompt, prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )

        await session.delete(prompt)
        await session.commit()

# Prompt templates and categories
@router.get("/templates")
async def get_prompt_templates():
    """Get available prompt templates."""
    return {
        "strategy": {
            "competitor_analysis": {
                "title": "Competitor Analysis",
                "content": "Analyze the following competitors for {company_name}:\n{competitors}\n\nFocus on:\n- Key differentiators\n- Market positioning\n- Content strategy\n- Community engagement",
                "variables": ["company_name", "competitors"]
            },
            "content_strategy": {
                "title": "Content Strategy",
                "content": "Create a content strategy for {company_name} targeting {audience}:\n\nInclude:\n- Content themes\n- Publishing schedule\n- Distribution channels\n- Success metrics",
                "variables": ["company_name", "audience"]
            }
        },
        "content": {
            "blog_post": {
                "title": "Blog Post Generator",
                "content": "Write a blog post about {topic} for {audience}:\n\nRequirements:\n- Engaging introduction\n- Clear structure\n- Actionable insights\n- SEO optimization",
                "variables": ["topic", "audience"]
            },
            "tutorial": {
                "title": "Tutorial Creator",
                "content": "Create a tutorial for {technology} covering {topic}:\n\nInclude:\n- Prerequisites\n- Step-by-step instructions\n- Code examples\n- Troubleshooting tips",
                "variables": ["technology", "topic"]
            }
        },
        "community": {
            "engagement_plan": {
                "title": "Community Engagement Plan",
                "content": "Develop an engagement plan for {platform} community:\n\nFocus on:\n- Content calendar\n- Engagement metrics\n- Growth strategies\n- Community guidelines",
                "variables": ["platform"]
            }
        },
        "analytics": {
            "performance_report": {
                "title": "Performance Report",
                "content": "Generate a performance report for {campaign}:\n\nInclude:\n- Key metrics\n- Insights\n- Recommendations\n- Next steps",
                "variables": ["campaign"]
            }
        }
    }

@router.get("/categories")
async def get_prompt_categories():
    """Get available prompt categories."""
    return {
        "strategy": {
            "description": "Strategic planning and analysis prompts",
            "examples": ["competitor analysis", "market research", "content strategy"]
        },
        "content": {
            "description": "Content creation and writing prompts",
            "examples": ["blog posts", "tutorials", "documentation"]
        },
        "community": {
            "description": "Community management and engagement prompts",
            "examples": ["engagement plans", "social media", "community guidelines"]
        },
        "analytics": {
            "description": "Data analysis and reporting prompts",
            "examples": ["performance reports", "metrics analysis", "insights"]
        },
        "general": {
            "description": "General purpose prompts",
            "examples": ["brainstorming", "planning", "ideation"]
        }
    }

# Prompt analytics
@router.get("/analytics", response_model=PromptAnalytics)
async def get_prompt_analytics(
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
):
    """Get prompt analytics."""
    async with SessionLocal() as session:
        query = select(Prompt)
        if project_id:
            query = query.where(Prompt.project_id == project_id)

        result = await session.execute(query)
        prompts = result.scalars().all()

        # Count by category
        prompts_by_category = {}
        for prompt in prompts:
            category = prompt.category.value
            prompts_by_category[category] = prompts_by_category.get(category, 0) + 1

        # Get most used prompts (mock data for now)
        most_used = [
            PromptResponse(
                id=prompt.id,
                project_id=prompt.project_id,
                title=prompt.title,
                content=prompt.content,
                category=prompt.category,
                prompt_type=prompt.prompt_type,
                tags=prompt.tags or [],
                metadata=prompt.metadata or {},
                is_public=prompt.is_public,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at,
                usage_count=0,
                avg_rating=None
            )
            for prompt in prompts[:5]
        ]

        return PromptAnalytics(
            total_prompts=len(prompts),
            prompts_by_category=prompts_by_category,
            most_used_prompts=most_used,
            avg_usage_per_prompt=0.0  # Would need usage tracking
        )

# Prompt search and discovery
@router.get("/search")
async def search_prompts(
    q: str,
    category: Optional[PromptCategory] = None,
    project_id: Optional[UUID] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Search prompts by content and title."""
    async with SessionLocal() as session:
        query = select(Prompt).where(
            (Prompt.title.ilike(f"%{q}%")) |
            (Prompt.content.ilike(f"%{q}%")) |
            (Prompt.tags.any(q))
        )

        if category:
            query = query.where(Prompt.category == category)
        if project_id:
            query = query.where(Prompt.project_id == project_id)

        query = query.limit(limit)
        result = await session.execute(query)
        prompts = result.scalars().all()

        return [
            PromptResponse(
                id=prompt.id,
                project_id=prompt.project_id,
                title=prompt.title,
                content=prompt.content,
                category=prompt.category,
                prompt_type=prompt.prompt_type,
                tags=prompt.tags or [],
                metadata=prompt.metadata or {},
                is_public=prompt.is_public,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at,
                usage_count=0,
                avg_rating=None
            )
            for prompt in prompts
        ]

# Prompt sharing and collaboration
@router.post("/{prompt_id}/share")
async def share_prompt(
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Share a prompt (make it public)."""
    async with SessionLocal() as session:
        prompt = await session.get(Prompt, prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )

        prompt.is_public = True
        await session.commit()

        return {"message": "Prompt shared successfully"}

@router.post("/{prompt_id}/duplicate")
async def duplicate_prompt(
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Duplicate a prompt."""
    async with SessionLocal() as session:
        original = await session.get(Prompt, prompt_id)
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )

        # Create duplicate
        duplicate = Prompt(
            project_id=original.project_id,
            title=f"{original.title} (Copy)",
            content=original.content,
            category=original.category,
            prompt_type=original.prompt_type,
            tags=original.tags or [],
            metadata=original.metadata or {},
            is_public=False
        )

        session.add(duplicate)
        await session.commit()
        await session.refresh(duplicate)

        return PromptResponse(
            id=duplicate.id,
            project_id=duplicate.project_id,
            title=duplicate.title,
            content=duplicate.content,
            category=duplicate.category,
            prompt_type=duplicate.prompt_type,
            tags=duplicate.tags or [],
            metadata=duplicate.metadata or {},
            is_public=duplicate.is_public,
            created_at=duplicate.created_at,
            updated_at=duplicate.updated_at,
            usage_count=0,
            avg_rating=None
        )
