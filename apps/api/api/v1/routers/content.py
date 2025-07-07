from fastapi import APIRouter
from db.base import SessionLocal
from db.models.content_item import ContentItem

router = APIRouter()

@router.get("/content/{id}")
async def get_content(id: str):
    async with SessionLocal() as session:
        item = await session.get(ContentItem, id)
        return {"html": item.html}
