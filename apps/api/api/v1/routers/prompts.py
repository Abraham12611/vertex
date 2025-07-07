from fastapi import APIRouter, Depends
from api.v1.deps import get_current_user

router = APIRouter()

@router.get("/")
async def get_prompts(user=Depends(get_current_user)):
    return []
