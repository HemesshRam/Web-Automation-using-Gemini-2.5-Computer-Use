"""
Log Routes — Task-specific and recent logs
"""

from fastapi import APIRouter, Query
from api.services import LogService
from api.schemas import LogEntry
from typing import List

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])

log_service = LogService()


@router.get("/recent", response_model=List[LogEntry])
def get_recent_logs(lines: int = Query(200, ge=10, le=2000)):
    """Get recent log entries from latest log file"""
    return log_service.get_recent_logs(lines=lines)


@router.get("/{task_id}", response_model=List[LogEntry])
def get_task_logs(task_id: str):
    """Get logs for a specific task"""
    return log_service.get_task_logs(task_id)
