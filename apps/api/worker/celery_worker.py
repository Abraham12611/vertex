from celery import Celery, chain

celery_app = Celery(
    "vertex_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def run_strategy_task(flow_id, project_id, prompt):
    # Run strategy agent, save output to DB
    ...

@celery_app.task
def run_content_task(flow_id, project_id):
    # Run content agent, save output to DB
    ...

@celery_app.task
def run_community_task(flow_id, project_id):
    # Run community agent, save output to DB
    ...

@celery_app.task
def run_analytics_task(flow_id, project_id):
    # Run analytics agent, save output to DB
    ...

@celery_app.task
def run_flow_task(flow_id, project_id, prompt):
    return chain(
        run_strategy_task.s(flow_id, project_id, prompt),
        run_content_task.s(flow_id, project_id),
        run_community_task.s(flow_id, project_id),
        run_analytics_task.s(flow_id, project_id)
    )()
