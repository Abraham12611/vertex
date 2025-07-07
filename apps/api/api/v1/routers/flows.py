from fastapi import APIRouter, BackgroundTasks, Depends
from uuid import UUID
from api.v1.deps import get_current_user
from flows.devrel_flow import get_devrel_flow
from worker.celery_worker import run_flow_task

router = APIRouter()

@router.post("/projects/{project_id}/run-flow")
async def run_flow(project_id: UUID, prompt: str, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    # Save flow row, enqueue Celery chain
    flow_id = ... # generate and save flow row in DB
    background_tasks.add_task(run_flow_task.delay, flow_id, project_id, prompt)
    return {"flow_id": str(flow_id), "status": "queued"}
