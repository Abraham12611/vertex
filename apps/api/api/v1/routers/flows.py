from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from api.v1.deps import get_current_user
from db.base import SessionLocal
from db.models.user import User
from db.models.task import Task, TaskStatus
from db.models.project import Project
from flows.devrel_flow import get_devrel_flow
from worker.celery_worker import run_flow_task
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()

# Pydantic models
class FlowStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class FlowType(str, Enum):
    devrel_strategy = "devrel_strategy"
    content_generation = "content_generation"
    competitor_analysis = "competitor_analysis"
    community_engagement = "community_engagement"
    analytics_report = "analytics_report"

class FlowCreate(BaseModel):
    project_id: UUID
    flow_type: FlowType
    prompt: str
    parameters: Optional[Dict[str, Any]] = None
    priority: Optional[int] = 1

class FlowUpdate(BaseModel):
    status: Optional[FlowStatus] = None
    parameters: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None

class FlowResponse(BaseModel):
    id: UUID
    project_id: UUID
    flow_type: FlowType
    prompt: str
    status: FlowStatus
    parameters: Dict[str, Any] = {}
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class TaskResponse(BaseModel):
    id: UUID
    flow_id: UUID
    task_type: str
    status: TaskStatus
    input_data: Dict[str, Any] = {}
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class FlowAnalytics(BaseModel):
    total_flows: int
    success_rate: float
    avg_execution_time: float
    flows_by_type: Dict[str, int]
    recent_flows: List[FlowResponse]

# Flow CRUD operations
@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    flow_data: FlowCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow."""
    async with SessionLocal() as session:
        # Verify project exists
        project = await session.get(Project, flow_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Create flow record
        flow = Task(
            project_id=flow_data.project_id,
            flow_type=flow_data.flow_type,
            prompt=flow_data.prompt,
            status=FlowStatus.pending,
            parameters=flow_data.parameters or {},
            priority=flow_data.priority
        )
        session.add(flow)
        await session.commit()
        await session.refresh(flow)

        # Start flow execution in background
        background_tasks.add_task(run_flow_task.delay, str(flow.id), flow_data.project_id, flow_data.prompt)

        return FlowResponse(
            id=flow.id,
            project_id=flow.project_id,
            flow_type=flow.flow_type,
            prompt=flow.prompt,
            status=flow.status,
            parameters=flow.parameters,
            priority=flow.priority,
            created_at=flow.created_at,
            started_at=None,
            completed_at=None,
            result=None,
            error=None,
            execution_time=None
        )

@router.get("/", response_model=List[FlowResponse])
async def list_flows(
    project_id: Optional[UUID] = None,
    flow_type: Optional[FlowType] = None,
    status: Optional[FlowStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """List workflows with optional filters."""
    async with SessionLocal() as session:
        query = select(Task)

        if project_id:
            query = query.where(Task.project_id == project_id)
        if flow_type:
            query = query.where(Task.flow_type == flow_type)
        if status:
            query = query.where(Task.status == status)

        query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        flows = result.scalars().all()

        return [
            FlowResponse(
                id=flow.id,
                project_id=flow.project_id,
                flow_type=flow.flow_type,
                prompt=flow.prompt,
                status=flow.status,
                parameters=flow.parameters or {},
                priority=flow.priority,
                created_at=flow.created_at,
                started_at=flow.started_at,
                completed_at=flow.completed_at,
                result=flow.result,
                error=flow.error,
                execution_time=flow.execution_time
            )
            for flow in flows
        ]

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get specific workflow by ID."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        return FlowResponse(
            id=flow.id,
            project_id=flow.project_id,
            flow_type=flow.flow_type,
            prompt=flow.prompt,
            status=flow.status,
            parameters=flow.parameters or {},
            priority=flow.priority,
            created_at=flow.created_at,
            started_at=flow.started_at,
            completed_at=flow.completed_at,
            result=flow.result,
            error=flow.error,
            execution_time=flow.execution_time
        )

@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: UUID,
    flow_data: FlowUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update workflow."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        if flow_data.status is not None:
            flow.status = flow_data.status
        if flow_data.parameters is not None:
            flow.parameters = flow_data.parameters
        if flow_data.priority is not None:
            flow.priority = flow_data.priority

        await session.commit()
        await session.refresh(flow)

        return FlowResponse(
            id=flow.id,
            project_id=flow.project_id,
            flow_type=flow.flow_type,
            prompt=flow.prompt,
            status=flow.status,
            parameters=flow.parameters or {},
            priority=flow.priority,
            created_at=flow.created_at,
            started_at=flow.started_at,
            completed_at=flow.completed_at,
            result=flow.result,
            error=flow.error,
            execution_time=flow.execution_time
        )

@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete workflow."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        await session.delete(flow)
        await session.commit()

# Flow execution and control
@router.post("/{flow_id}/run")
async def run_flow(
    flow_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Manually trigger flow execution."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        if flow.status in [FlowStatus.running, FlowStatus.completed]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Flow is already running or completed"
            )

        # Update status and start execution
        flow.status = FlowStatus.running
        flow.started_at = datetime.now()
        await session.commit()

        # Start execution in background
        background_tasks.add_task(run_flow_task.delay, str(flow.id), flow.project_id, flow.prompt)

        return {"message": "Flow execution started"}

@router.post("/{flow_id}/cancel")
async def cancel_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Cancel a running workflow."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        if flow.status != FlowStatus.running:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Flow is not running"
            )

        flow.status = FlowStatus.cancelled
        await session.commit()

        return {"message": "Flow cancelled successfully"}

# Flow monitoring
@router.get("/{flow_id}/status")
async def get_flow_status(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get real-time flow status."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        return {
            "flow_id": str(flow_id),
            "status": flow.status,
            "progress": 0,  # Would need to calculate based on subtasks
            "started_at": flow.started_at,
            "estimated_completion": None,  # Would need to calculate
            "current_step": None  # Would need to track
        }

@router.get("/{flow_id}/tasks", response_model=List[TaskResponse])
async def get_flow_tasks(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get all tasks for a workflow."""
    async with SessionLocal() as session:
        # Verify flow exists
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        # Get subtasks (in a real implementation, you'd have a separate subtasks table)
        # For now, return the main flow as a task
        return [
            TaskResponse(
                id=flow.id,
                flow_id=flow.id,
                task_type=flow.flow_type,
                status=flow.status,
                input_data={"prompt": flow.prompt, **flow.parameters},
                output_data={"result": flow.result} if flow.result else None,
                created_at=flow.created_at,
                started_at=flow.started_at,
                completed_at=flow.completed_at,
                error=flow.error
            )
        ]

# Flow analytics
@router.get("/analytics", response_model=FlowAnalytics)
async def get_flow_analytics(
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
):
    """Get workflow analytics."""
    async with SessionLocal() as session:
        # Count total flows
        query = select(Task)
        if project_id:
            query = query.where(Task.project_id == project_id)

        result = await session.execute(query)
        flows = result.scalars().all()
        total_flows = len(flows)

        # Calculate success rate
        successful_flows = len([f for f in flows if f.status == FlowStatus.completed])
        success_rate = (successful_flows / total_flows * 100) if total_flows > 0 else 0

        # Calculate average execution time
        completed_flows = [f for f in flows if f.status == FlowStatus.completed and f.execution_time]
        avg_execution_time = sum(f.execution_time for f in completed_flows) / len(completed_flows) if completed_flows else 0

        # Count flows by type
        flows_by_type = {}
        for flow in flows:
            flow_type = flow.flow_type
            flows_by_type[flow_type] = flows_by_type.get(flow_type, 0) + 1

        # Get recent flows
        recent_flows = [
            FlowResponse(
                id=flow.id,
                project_id=flow.project_id,
                flow_type=flow.flow_type,
                prompt=flow.prompt,
                status=flow.status,
                parameters=flow.parameters or {},
                priority=flow.priority,
                created_at=flow.created_at,
                started_at=flow.started_at,
                completed_at=flow.completed_at,
                result=flow.result,
                error=flow.error,
                execution_time=flow.execution_time
            )
            for flow in flows[:5]  # Last 5 flows
        ]

        return FlowAnalytics(
            total_flows=total_flows,
            success_rate=success_rate,
            avg_execution_time=avg_execution_time,
            flows_by_type=flows_by_type,
            recent_flows=recent_flows
        )

# Flow templates
@router.get("/templates")
async def get_flow_templates():
    """Get available workflow templates."""
    return {
        "devrel_strategy": {
            "name": "DevRel Strategy Generation",
            "description": "Generate comprehensive DevRel strategy with competitor analysis",
            "steps": [
                "Competitor research",
                "Keyword analysis",
                "Content planning",
                "Community strategy"
            ],
            "estimated_time": "30-45 minutes",
            "required_inputs": ["company_name", "target_audience", "goals"]
        },
        "content_generation": {
            "name": "Content Generation Pipeline",
            "description": "Generate blog posts, tutorials, and social content",
            "steps": [
                "Topic research",
                "Content outline",
                "Draft generation",
                "SEO optimization"
            ],
            "estimated_time": "15-30 minutes",
            "required_inputs": ["topic", "content_type", "target_audience"]
        },
        "competitor_analysis": {
            "name": "Competitor Analysis",
            "description": "Analyze competitors and market positioning",
            "steps": [
                "Competitor identification",
                "Feature comparison",
                "Market positioning",
                "Opportunity analysis"
            ],
            "estimated_time": "20-35 minutes",
            "required_inputs": ["product_name", "competitors", "market_focus"]
        },
        "community_engagement": {
            "name": "Community Engagement Strategy",
            "description": "Plan community building and engagement activities",
            "steps": [
                "Platform analysis",
                "Content calendar",
                "Engagement metrics",
                "Growth strategy"
            ],
            "estimated_time": "25-40 minutes",
            "required_inputs": ["community_platforms", "target_audience", "goals"]
        }
    }

# Flow execution history
@router.get("/{flow_id}/history")
async def get_flow_history(
    flow_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get execution history for a workflow."""
    async with SessionLocal() as session:
        flow = await session.get(Task, flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found"
            )

        # For demo, return basic history
        history = [
            {
                "timestamp": flow.created_at,
                "event": "flow_created",
                "details": f"Flow {flow.flow_type} created"
            }
        ]

        if flow.started_at:
            history.append({
                "timestamp": flow.started_at,
                "event": "flow_started",
                "details": "Flow execution started"
            })

        if flow.completed_at:
            history.append({
                "timestamp": flow.completed_at,
                "event": "flow_completed",
                "details": f"Flow completed with status: {flow.status}"
            })

        return {
            "flow_id": str(flow_id),
            "history": history
        }