from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from pydantic import BaseModel
from api.v1.deps import get_current_user
from agents.crew import get_crew

router = APIRouter()

class RunResult(BaseModel):
    result: str

@router.post("/{agent_id}/run", response_model=RunResult)
async def run_agent(agent_id: UUID, user=Depends(get_current_user)):
    # For demo, ignore agent_id and always run StrategyAgent
    crew = get_crew("Demo: Generate a DevRel strategy for a new SaaS product.")
    result = crew.kickoff()
    return RunResult(result=result)
