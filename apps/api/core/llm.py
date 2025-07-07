from groq import Groq
from functools import lru_cache
from pydantic import BaseModel
from typing import List
from core.settings import settings

class ChatMessage(BaseModel):
    role: str
    content: str

@lru_cache
def _client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)

async def chat_completion(
    messages: List[ChatMessage],
    model: str = "llama3-70b-8192",
    stream: bool = False
):
    return await _client().chat.completions.create(
        model=model,
        messages=[m.dict() for m in messages],
        stream=stream,
    )
