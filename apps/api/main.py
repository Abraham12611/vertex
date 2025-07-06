from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from api.v1.routers import (
    auth,
    prompts,
    health,
    agents,
    content,
    documents,
    flows,
    search,
    ws
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Vertex DevRel Platform...")
    yield
    # Shutdown
    print("🛑 Shutting down Vertex DevRel Platform...")

app = FastAPI(
    title="Vertex DevRel Platform API",
    description="AI-powered DevRel automation platform with multi-agent orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://vertex.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["Prompts"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(flows.router, prefix="/api/v1/flows", tags=["Workflows"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(ws.router, prefix="/api/v1/ws", tags=["WebSocket"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Vertex DevRel Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check (legacy endpoint)
@app.get("/health")
def health():
    return {"status": "ok", "service": "vertex-api"}

# Mock endpoints for frontend development
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
