from groq import Groq
from functools import lru_cache
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.settings import settings

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "llama3-70b-8192"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatCompletionResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, Any]

@lru_cache
def _client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)

async def chat_completion(
    messages: List[ChatMessage],
    model: str = "llama3-70b-8192",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False
) -> ChatCompletionResponse:
    """Send a chat completion request to Groq"""
    try:
        response = await _client().chat.completions.create(
            model=model,
            messages=[m.dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

        if stream:
            return response

        return ChatCompletionResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.dict() if response.usage else {}
        )
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

async def generate_content(prompt: str, model: str = "llama3-70b-8192") -> str:
    """Generate content using Groq"""
    messages = [ChatMessage(role="user", content=prompt)]
    response = await chat_completion(messages, model=model)
    return response.content

async def analyze_text(text: str, analysis_type: str = "summary") -> str:
    """Analyze text for different purposes"""
    prompts = {
        "summary": f"Summarize the following text in 2-3 sentences:\n\n{text}",
        "sentiment": f"Analyze the sentiment of this text (positive/negative/neutral):\n\n{text}",
        "keywords": f"Extract the top 5 keywords from this text:\n\n{text}",
        "tone": f"Analyze the tone of this text (professional/casual/technical):\n\n{text}"
    }

    prompt = prompts.get(analysis_type, prompts["summary"])
    return await generate_content(prompt)
