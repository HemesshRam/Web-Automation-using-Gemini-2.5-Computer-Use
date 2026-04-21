"""
Pydantic Response Schemas for Dashboard API
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DashboardStats(BaseModel):
    total_tasks: int = 0
    success_count: int = 0
    failed_count: int = 0
    timeout_count: int = 0
    running_count: int = 0
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    total_actions: int = 0
    total_iterations: int = 0
    avg_actions_per_task: float = 0.0
    websites_automated: List[str] = []


class TimelinePoint(BaseModel):
    date: str
    success_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    avg_time: float = 0.0


class TaskSummary(BaseModel):
    task_id: str
    prompt: str = ""
    target_url: Optional[str] = None
    actual_url: Optional[str] = None
    status: str = "unknown"
    total_iterations: int = 0
    total_actions: int = 0
    execution_time: float = 0.0
    pages_visited: int = 0
    website_type: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class StepDetail(BaseModel):
    iteration: int
    action_type: Optional[str] = None
    target: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: Optional[str] = None


class TaskDetail(BaseModel):
    task_id: str
    prompt: str = ""
    target_url: Optional[str] = None
    actual_url: Optional[str] = None
    status: str = "unknown"
    total_iterations: int = 0
    total_actions: int = 0
    execution_time: float = 0.0
    pages_visited: int = 0
    website_type: Optional[str] = None
    ai_summary: Optional[str] = None
    gemini_used: bool = False
    fallback_used: bool = False
    engine: Optional[str] = None
    screenshot_directory: Optional[str] = None
    navigation_url: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    steps: List[StepDetail] = []
    unique_pages: List[str] = []
    errors: Optional[str] = None
    raw_json: Optional[dict] = None


class LogEntry(BaseModel):
    timestamp: Optional[str] = None
    level: str = "INFO"
    component: str = ""
    message: str = ""


class ScreenshotInfo(BaseModel):
    filename: str
    path: str
    url: str
    size_bytes: int = 0
    step_number: Optional[int] = None


class SettingsResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    browser_type: str
    headless: bool
    window_width: int
    window_height: int
    anti_bot_enabled: bool
    database_url: str
    log_level: str
    gemini_model: str
    computer_use_model: str
    screenshots_enabled: bool
    max_retry_attempts: int
