from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.agent import Agent, AgentType
from db.models.project import Project
from agents.crew import get_crew
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models
class AgentStatus(str, Enum):
    online = "online"
    offline = "offline"
    busy = "busy"
    error = "error"

class AgentConfig(BaseModel):
    model: str = "groq-llama3-8b-8192"
    temperature: float = 0.7
    max_tokens: int = 4000
    tools: List[str] = []
    custom_prompt: Optional[str] = None

class AgentCreate(BaseModel):
    project_id: UUID
    type: AgentType
    config: Optional[AgentConfig] = None

class AgentUpdate(BaseModel):
    config: Optional[AgentConfig] = None
    status: Optional[AgentStatus] = None

class AgentResponse(BaseModel):
    id: UUID
    project_id: UUID
    type: AgentType
    config: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    last_active: Optional[datetime] = None

class RunAgentRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = 300

class RunAgentResponse(BaseModel):
    agent_id: UUID
    result: str
    execution_time: float
    tokens_used: Optional[int] = None
    status: str

class AgentStats(BaseModel):
    total_runs: int
    success_rate: float
    avg_execution_time: float
    last_run: Optional[datetime] = None

# Agent CRUD operations
@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new agent for a project."""
    async with SessionLocal() as session:
        # Verify project exists and user has access
        project = await session.get(Project, agent_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Create agent
        agent = Agent(
            project_id=agent_data.project_id,
            type=agent_data.type,
            config=agent_data.config.dict() if agent_data.config else None,
            status="offline"
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        return AgentResponse(
            id=agent.id,
            project_id=agent.project_id,
            type=agent.type,
            config=agent.config,
            status=agent.status,
            created_at=agent.created_at,
            last_active=None
        )

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    project_id: Optional[UUID] = None,
    agent_type: Optional[AgentType] = None,
    current_user: User = Depends(get_current_user)
):
    """List all agents, optionally filtered by project and type."""
    async with SessionLocal() as session:
        query = select(Agent)

        if project_id:
            query = query.where(Agent.project_id == project_id)
        if agent_type:
            query = query.where(Agent.type == agent_type)

        result = await session.execute(query)
        agents = result.scalars().all()

        return [
            AgentResponse(
                id=agent.id,
                project_id=agent.project_id,
                type=agent.type,
                config=agent.config,
                status=agent.status,
                created_at=agent.created_at,
                last_active=None
            )
            for agent in agents
        ]

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific agent by ID."""
    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        return AgentResponse(
            id=agent.id,
            project_id=agent.project_id,
            type=agent.type,
            config=agent.config,
            status=agent.status,
            created_at=agent.created_at,
            last_active=None
        )

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an agent's configuration and status."""
    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        if agent_data.config is not None:
            agent.config = agent_data.config.dict()
        if agent_data.status is not None:
            agent.status = agent_data.status

        await session.commit()
        await session.refresh(agent)

        return AgentResponse(
            id=agent.id,
            project_id=agent.project_id,
            type=agent.type,
            config=agent.config,
            status=agent.status,
            created_at=agent.created_at,
            last_active=None
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete an agent."""
    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        await session.delete(agent)
        await session.commit()

# Agent execution
@router.post("/{agent_id}/run", response_model=RunAgentResponse)
async def run_agent(
    agent_id: UUID,
    request: RunAgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Run an agent with a specific prompt."""
    import time
    start_time = time.time()

    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        # Update agent status to busy
        agent.status = "busy"
        await session.commit()

        try:
            # For demo, use the crew system
            crew = get_crew(f"Agent Type: {agent.type.value}\nPrompt: {request.prompt}")
            result = crew.kickoff()

            execution_time = time.time() - start_time

            # Update agent status back to online
            agent.status = "online"
            await session.commit()

            return RunAgentResponse(
                agent_id=agent_id,
                result=result,
                execution_time=execution_time,
                tokens_used=None,
                status="completed"
            )

        except Exception as e:
            # Update agent status to error
            agent.status = "error"
            await session.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent execution failed: {str(e)}"
            )

@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Stop a running agent."""
    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        agent.status = "offline"
        await session.commit()

        return {"message": "Agent stopped successfully"}

# Agent monitoring and analytics
@router.get("/{agent_id}/stats", response_model=AgentStats)
async def get_agent_stats(
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get agent performance statistics."""
    # For demo, return mock stats
    return AgentStats(
        total_runs=42,
        success_rate=0.95,
        avg_execution_time=2.3,
        last_run=datetime.now()
    )

@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get real-time agent status."""
    async with SessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        return {
            "agent_id": str(agent_id),
            "status": agent.status,
            "type": agent.type.value,
            "last_active": None,
            "is_healthy": agent.status != "error"
        }

# Agent types and capabilities
@router.get("/types")
async def get_agent_types():
    """Get available agent types and their capabilities."""
    return {
        "strategy": {
            "description": "Competitor analysis, keyword research, content planning",
            "capabilities": ["Moz API integration", "SEO analysis", "Content calendar"],
            "tools": ["web_search", "moz_api", "trend_analysis"]
        },
        "content": {
            "description": "Technical content generation, documentation, code samples",
            "capabilities": ["Blog writing", "API docs", "Tutorial creation"],
            "tools": ["markdown_generator", "code_generator", "content_templates"]
        },
        "community": {
            "description": "Social media engagement, community management",
            "capabilities": ["Social posting", "Discord/Slack integration", "Community responses"],
            "tools": ["social_media_api", "discord_bot", "slack_bot"]
        },
        "analytics": {
            "description": "Performance tracking, metrics analysis, optimization",
            "capabilities": ["Performance reports", "Optimization recommendations", "ROI tracking"],
            "tools": ["analytics_api", "data_visualization", "report_generator"]
        }
    }
