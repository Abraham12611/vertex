from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok", "db": True, "redis": True}
