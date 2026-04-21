"""
Task Routes — List, Detail, Steps
"""

from fastapi import APIRouter, HTTPException, Query
from api.services import TaskService
from api.schemas import TaskSummary, TaskDetail
from typing import List, Optional

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

task_service = TaskService()


@router.get("", response_model=List[TaskSummary])
def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get paginated list of all tasks"""
    return task_service.get_all_tasks(status=status, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskDetail)
def get_task_detail(task_id: str):
    """Get full task detail including steps, AI summary, and raw JSON"""
    detail = task_service.get_task_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return detail
