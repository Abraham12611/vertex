from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routers import auth, prompts, health

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/mock/prompts")
def mock_prompts():
    return [
        {"id": 1, "prompt": "How do I integrate Groq with FastAPI?", "date": "2024-06-01"},
        {"id": 2, "prompt": "Generate a content calendar for June.", "date": "2024-06-01"},
        {"id": 3, "prompt": "List top 5 competitors.", "date": "2024-05-31"},
        {"id": 4, "prompt": "Draft onboarding email.", "date": "2024-05-30"},
        {"id": 5, "prompt": "Summarize latest analytics.", "date": "2024-05-29"},
    ]

@app.get("/mock/agents")
def mock_agents():
    return [
        {"name": "Strategy Agent", "status": "online"},
        {"name": "Content Agent", "status": "online"},
        {"name": "Community Agent", "status": "online"},
        {"name": "Analytics Agent", "status": "online"},
    ]

@app.get("/mock/analytics")
def mock_analytics():
    return {
        "campaigns": [],
        "message": "No analytics data yet. Run your first campaign!"
    }

@app.get("/mock/settings")
def mock_settings():
    return {
        "profile": {"name": "Jane Doe", "email": "jane@example.com"},
        "project": {"name": "Vertex Project", "id": "vertex-001"},
        "billing": {"plan": "Pro", "renewal": "2024-12-01"}
    }
