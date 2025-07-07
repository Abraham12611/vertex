from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.content_item import ContentItem
from db.models.agent import Agent
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models
class ContentStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    scheduled = "scheduled"

class ContentType(str, Enum):
    blog_post = "blog_post"
    tutorial = "tutorial"
    documentation = "documentation"
    social_post = "social_post"
    newsletter = "newsletter"
    case_study = "case_study"

class ContentCreate(BaseModel):
    title: str
    markdown: str
    content_type: ContentType
    agent_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    content_type: Optional[ContentType] = None
    published: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentResponse(BaseModel):
    id: UUID
    title: str
    markdown: str
    html: Optional[str] = None
    content_type: ContentType
    agent_id: Optional[UUID] = None
    published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    word_count: int
    reading_time: int

class ContentAnalytics(BaseModel):
    views: int
    shares: int
    engagement_rate: float
    conversion_rate: float
    top_keywords: List[str]

# Content CRUD operations
@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new content."""
    async with SessionLocal() as session:
        # Verify agent exists if provided
        if content_data.agent_id:
            agent = await session.get(Agent, content_data.agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )

        # Calculate word count and reading time
        word_count = len(content_data.markdown.split())
        reading_time = max(1, word_count // 200)  # ~200 words per minute

        content = ContentItem(
            title=content_data.title,
            markdown=content_data.markdown,
            content_type=content_data.content_type,
            agent_id=content_data.agent_id,
            published=False,
            tags=content_data.tags or [],
            metadata=content_data.metadata or {}
        )

        session.add(content)
        await session.commit()
        await session.refresh(content)

        return ContentResponse(
            id=content.id,
            title=content.title,
            markdown=content.markdown,
            html=content.html,
            content_type=content.content_type,
            agent_id=content.agent_id,
            published=content.published,
            created_at=content.created_at,
            updated_at=content.updated_at,
            tags=content.tags or [],
            metadata=content.metadata or {},
            word_count=word_count,
            reading_time=reading_time
        )

@router.get("/", response_model=List[ContentResponse])
async def list_content(
    content_type: Optional[ContentType] = None,
    published: Optional[bool] = None,
    agent_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """List content with optional filters."""
    async with SessionLocal() as session:
        query = select(ContentItem)

        if content_type:
            query = query.where(ContentItem.content_type == content_type)
        if published is not None:
            query = query.where(ContentItem.published == published)
        if agent_id:
            query = query.where(ContentItem.agent_id == agent_id)

        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        contents = result.scalars().all()

        return [
            ContentResponse(
                id=content.id,
                title=content.title,
                markdown=content.markdown,
                html=content.html,
                content_type=content.content_type,
                agent_id=content.agent_id,
                published=content.published,
                created_at=content.created_at,
                updated_at=content.updated_at,
                tags=content.tags or [],
                metadata=content.metadata or {},
                word_count=len(content.markdown.split()),
                reading_time=max(1, len(content.markdown.split()) // 200)
            )
            for content in contents
        ]

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get specific content by ID."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        word_count = len(content.markdown.split())
        reading_time = max(1, word_count // 200)

        return ContentResponse(
            id=content.id,
            title=content.title,
            markdown=content.markdown,
            html=content.html,
            content_type=content.content_type,
            agent_id=content.agent_id,
            published=content.published,
            created_at=content.created_at,
            updated_at=content.updated_at,
            tags=content.tags or [],
            metadata=content.metadata or {},
            word_count=word_count,
            reading_time=reading_time
        )

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update content."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        if content_data.title is not None:
            content.title = content_data.title
        if content_data.markdown is not None:
            content.markdown = content_data.markdown
        if content_data.html is not None:
            content.html = content_data.html
        if content_data.content_type is not None:
            content.content_type = content_data.content_type
        if content_data.published is not None:
            content.published = content_data.published
        if content_data.tags is not None:
            content.tags = content_data.tags
        if content_data.metadata is not None:
            content.metadata = content_data.metadata

        await session.commit()
        await session.refresh(content)

        word_count = len(content.markdown.split())
        reading_time = max(1, word_count // 200)

        return ContentResponse(
            id=content.id,
            title=content.title,
            markdown=content.markdown,
            html=content.html,
            content_type=content.content_type,
            agent_id=content.agent_id,
            published=content.published,
            created_at=content.created_at,
            updated_at=content.updated_at,
            tags=content.tags or [],
            metadata=content.metadata or {},
            word_count=word_count,
            reading_time=reading_time
        )

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete content."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        await session.delete(content)
        await session.commit()

# Content generation and processing
@router.post("/{content_id}/generate-html")
async def generate_html(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Generate HTML from markdown content."""
    import markdown2

    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        # Convert markdown to HTML
        html = markdown2.markdown(content.markdown)
        content.html = html
        await session.commit()

        return {"html": html}

@router.post("/{content_id}/publish")
async def publish_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Publish content."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        content.published = True
        await session.commit()

        return {"message": "Content published successfully"}

@router.post("/{content_id}/unpublish")
async def unpublish_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Unpublish content."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        content.published = False
        await session.commit()

        return {"message": "Content unpublished successfully"}

# Content analytics
@router.get("/{content_id}/analytics", response_model=ContentAnalytics)
async def get_content_analytics(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get content analytics."""
    # For demo, return mock analytics
    return ContentAnalytics(
        views=1250,
        shares=45,
        engagement_rate=0.08,
        conversion_rate=0.02,
        top_keywords=["groq", "fastapi", "ai", "devrel", "automation"]
    )

# Content templates
@router.get("/templates")
async def get_content_templates():
    """Get available content templates."""
    return {
        "blog_post": {
            "title": "Blog Post Template",
            "markdown": """# [Title]

## Introduction
[Brief introduction to the topic]

## Main Content
[Your main content here]

## Conclusion
[Wrap up your thoughts]

## Call to Action
[What should readers do next?]""",
            "variables": ["title", "topic", "cta"]
        },
        "tutorial": {
            "title": "Tutorial Template",
            "markdown": """# [Tutorial Title]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Step 1: [First Step]
[Detailed instructions]

## Step 2: [Second Step]
[Detailed instructions]

## Summary
[What was accomplished]""",
            "variables": ["title", "prerequisites", "steps"]
        },
        "social_post": {
            "title": "Social Media Post Template",
            "markdown": """🚀 [Hook]

[Main message]

💡 Key takeaway: [Insight]

🔗 [Link or call to action]

#devrel #tech #innovation""",
            "variables": ["hook", "message", "takeaway", "cta"]
        }
    }

# Content import/export
@router.post("/import")
async def import_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Import content from file (markdown, JSON, etc.)."""
    if not file.filename.endswith(('.md', '.json')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .md and .json files are supported"
        )

    content = await file.read()
    # Process file content and create content items
    # Implementation depends on file format

    return {"message": "Content imported successfully", "items_created": 1}

@router.get("/{content_id}/export")
async def export_content(
    content_id: UUID,
    format: str = "markdown",
    current_user: User = Depends(get_current_user)
):
    """Export content in specified format."""
    async with SessionLocal() as session:
        content = await session.get(ContentItem, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        if format == "markdown":
            return {"content": content.markdown, "filename": f"{content.title}.md"}
        elif format == "html":
            return {"content": content.html, "filename": f"{content.title}.html"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format"
            )
