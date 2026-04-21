"""
Screenshot Routes — Serve task screenshots
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from api.services import ScreenshotService
from api.schemas import ScreenshotInfo
from typing import List

router = APIRouter(prefix="/api/v1/screenshots", tags=["Screenshots"])

screenshot_service = ScreenshotService()


@router.get("/{task_id}", response_model=List[ScreenshotInfo])
def get_task_screenshots(task_id: str):
    """List all screenshots for a task"""
    return screenshot_service.get_task_screenshots(task_id)


@router.get("/{task_id}/{filename}")
def get_screenshot_file(task_id: str, filename: str):
    """Serve a specific screenshot image"""
    path = screenshot_service.get_screenshot_path(task_id, filename)
    if not path:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(path, media_type="image/png")
