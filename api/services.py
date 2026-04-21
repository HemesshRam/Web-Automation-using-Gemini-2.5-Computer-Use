"""
Dashboard Services — Business Logic & Data Aggregation
Reads from SQLite (via SQLAlchemy) + JSON execution result files
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from collections import Counter

from sqlalchemy import func
from persistence.database import get_session
from persistence.models import TaskMetadata, ExecutionHistory, URLHistory, AutomationLog
from api.schemas import (
    DashboardStats, TimelinePoint, TaskSummary, TaskDetail,
    StepDetail, LogEntry, ScreenshotInfo, SettingsResponse
)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
EXECUTION_RESULTS_DIR = PROJECT_ROOT / "execution_results"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"


class DashboardService:
    """Aggregates data from DB + filesystem for dashboard KPIs"""

    def get_stats(self) -> DashboardStats:
        session = get_session()
        try:
            # Counts from DB
            total = session.query(func.count(TaskMetadata.id)).scalar() or 0
            success = session.query(func.count(TaskMetadata.id)).filter(
                TaskMetadata.status == "success"
            ).scalar() or 0
            failed = session.query(func.count(TaskMetadata.id)).filter(
                TaskMetadata.status == "failed"
            ).scalar() or 0
            timeout = session.query(func.count(TaskMetadata.id)).filter(
                TaskMetadata.status == "timeout"
            ).scalar() or 0
            running = session.query(func.count(TaskMetadata.id)).filter(
                TaskMetadata.status == "running"
            ).scalar() or 0

            avg_time = session.query(func.avg(TaskMetadata.execution_time)).scalar() or 0.0
            total_actions = session.query(func.sum(TaskMetadata.total_actions)).scalar() or 0
            total_iterations = session.query(func.sum(TaskMetadata.total_iterations)).scalar() or 0

            # If DB is empty, count from JSON files
            if total == 0:
                total, success, failed, avg_time, total_actions, total_iterations = self._stats_from_json()
                timeout = 0
                running = 0

            # Website types from JSON files
            websites = self._get_website_types()

            success_rate = (success / total * 100) if total > 0 else 0.0
            avg_actions = (total_actions / total) if total > 0 else 0.0

            return DashboardStats(
                total_tasks=total,
                success_count=success,
                failed_count=failed,
                timeout_count=timeout,
                running_count=running,
                success_rate=round(success_rate, 1),
                avg_execution_time=round(float(avg_time), 1),
                total_actions=int(total_actions),
                total_iterations=int(total_iterations),
                avg_actions_per_task=round(avg_actions, 1),
                websites_automated=websites,
            )
        finally:
            session.close()

    def get_timeline(self, days: int = 30) -> List[TimelinePoint]:
        session = get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            tasks = session.query(TaskMetadata).filter(
                TaskMetadata.created_at >= cutoff
            ).order_by(TaskMetadata.created_at).all()

            # Group by date
            daily: Dict[str, Dict] = {}
            for task in tasks:
                date_str = task.created_at.strftime("%Y-%m-%d") if task.created_at else "unknown"
                if date_str not in daily:
                    daily[date_str] = {"success": 0, "failed": 0, "total": 0, "times": []}
                daily[date_str]["total"] += 1
                if task.status == "success":
                    daily[date_str]["success"] += 1
                else:
                    daily[date_str]["failed"] += 1
                if task.execution_time:
                    daily[date_str]["times"].append(task.execution_time)

            # If DB empty, build from JSON
            if not daily:
                daily = self._timeline_from_json(days)

            result = []
            for date_str in sorted(daily.keys()):
                d = daily[date_str]
                times = d.get("times", [])
                result.append(TimelinePoint(
                    date=date_str,
                    success_count=d["success"],
                    failed_count=d["failed"],
                    total_count=d["total"],
                    avg_time=round(sum(times) / len(times), 1) if times else 0.0,
                ))
            return result
        finally:
            session.close()

    def _stats_from_json(self):
        """Fallback: compute stats from JSON files when DB is empty"""
        total = 0
        success = 0
        failed = 0
        times = []
        actions = 0
        iterations = 0

        if EXECUTION_RESULTS_DIR.exists():
            for f in EXECUTION_RESULTS_DIR.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    total += 1
                    if data.get("status") == "success" or data.get("success"):
                        success += 1
                    else:
                        failed += 1
                    times.append(data.get("execution_time", 0))
                    actions += data.get("total_actions", 0)
                    iterations += data.get("total_iterations", 0)
                except Exception:
                    continue

        avg_time = sum(times) / len(times) if times else 0.0
        return total, success, failed, avg_time, actions, iterations

    def _timeline_from_json(self, days: int) -> Dict:
        """Build timeline data from JSON files"""
        daily: Dict[str, Dict] = {}
        if EXECUTION_RESULTS_DIR.exists():
            for f in EXECUTION_RESULTS_DIR.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    ts = data.get("timestamp", "")
                    if ts:
                        date_str = ts[:10]
                    else:
                        # Extract date from filename
                        match = re.search(r"(\d{8})", f.stem)
                        date_str = f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:8]}" if match else "unknown"

                    if date_str not in daily:
                        daily[date_str] = {"success": 0, "failed": 0, "total": 0, "times": []}
                    daily[date_str]["total"] += 1
                    if data.get("status") == "success" or data.get("success"):
                        daily[date_str]["success"] += 1
                    else:
                        daily[date_str]["failed"] += 1
                    daily[date_str]["times"].append(data.get("execution_time", 0))
                except Exception:
                    continue
        return daily

    def _get_website_types(self) -> List[str]:
        """Extract unique website types from JSON results"""
        types = set()
        if EXECUTION_RESULTS_DIR.exists():
            for f in EXECUTION_RESULTS_DIR.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    wt = data.get("website_type")
                    if wt:
                        types.add(wt)
                    else:
                        # Infer from URL
                        url = data.get("navigation_url", "") or data.get("target_url", "")
                        if "youtube" in url:
                            types.add("youtube")
                        elif "amazon" in url:
                            types.add("amazon")
                        elif "demoqa" in url:
                            types.add("demoqa")
                        elif "yahoo" in url:
                            types.add("yahoo_finance")
                except Exception:
                    continue
        return sorted(types)


class TaskService:
    """Task retrieval and detail assembly"""

    def get_all_tasks(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[TaskSummary]:
        # Try DB first
        session = get_session()
        try:
            query = session.query(TaskMetadata).order_by(TaskMetadata.created_at.desc())
            if status:
                query = query.filter(TaskMetadata.status == status)
            tasks = query.offset(offset).limit(limit).all()

            if tasks:
                return [self._task_to_summary(t) for t in tasks]
        finally:
            session.close()

        # Fallback to JSON files
        return self._tasks_from_json(status, limit, offset)

    def get_task_detail(self, task_id: str) -> Optional[TaskDetail]:
        # Load from DB
        session = get_session()
        try:
            task = session.query(TaskMetadata).filter_by(task_id=task_id).first()

            # Load JSON data
            json_data = self._load_json_for_task(task_id)

            if not task and not json_data:
                return None

            # Build detail
            detail = TaskDetail(
                task_id=task_id,
                prompt=getattr(task, 'prompt', '') or json_data.get('prompt', ''),
                target_url=getattr(task, 'target_url', None) or json_data.get('navigation_url'),
                actual_url=getattr(task, 'actual_url', None) or json_data.get('actual_url'),
                status=getattr(task, 'status', 'unknown') if task else json_data.get('status', 'unknown'),
                total_iterations=getattr(task, 'total_iterations', 0) if task else json_data.get('total_iterations', 0),
                total_actions=getattr(task, 'total_actions', 0) if task else json_data.get('total_actions', 0),
                execution_time=getattr(task, 'execution_time', 0) if task else json_data.get('execution_time', 0),
                pages_visited=getattr(task, 'pages_visited', 0) if task else len(json_data.get('unique_pages', [])),
                website_type=json_data.get('website_type'),
                ai_summary=json_data.get('ai_summary'),
                gemini_used=json_data.get('gemini_used', False),
                fallback_used=json_data.get('fallback_used', False),
                engine=json_data.get('engine'),
                screenshot_directory=json_data.get('screenshot_directory'),
                navigation_url=json_data.get('navigation_url'),
                created_at=task.created_at.isoformat() if task and task.created_at else json_data.get('timestamp'),
                completed_at=task.completed_at.isoformat() if task and task.completed_at else None,
                unique_pages=json_data.get('unique_pages', []),
                errors=task.errors if task else None,
                raw_json=json_data if json_data else None,
            )

            # Load step history from DB
            steps = session.query(ExecutionHistory).filter_by(
                task_id=task_id
            ).order_by(ExecutionHistory.timestamp).all()

            detail.steps = [
                StepDetail(
                    iteration=s.iteration or 0,
                    action_type=s.action_type,
                    target=s.target,
                    success=s.success or False,
                    error_message=s.error_message,
                    screenshot_path=s.screenshot_path,
                    timestamp=s.timestamp.isoformat() if s.timestamp else None,
                )
                for s in steps
            ]

            return detail
        finally:
            session.close()

    def _task_to_summary(self, task: TaskMetadata) -> TaskSummary:
        json_data = self._load_json_for_task(task.task_id)
        return TaskSummary(
            task_id=task.task_id,
            prompt=task.prompt or "",
            target_url=task.target_url,
            actual_url=task.actual_url,
            status=task.status or "unknown",
            total_iterations=task.total_iterations or 0,
            total_actions=task.total_actions or 0,
            execution_time=task.execution_time or 0.0,
            pages_visited=task.pages_visited or 0,
            website_type=json_data.get("website_type") if json_data else None,
            created_at=task.created_at.isoformat() if task.created_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
        )

    def _tasks_from_json(self, status: Optional[str], limit: int, offset: int) -> List[TaskSummary]:
        """Load tasks directly from JSON files when DB is empty"""
        results = []
        if EXECUTION_RESULTS_DIR.exists():
            files = sorted(EXECUTION_RESULTS_DIR.glob("*.json"), reverse=True)
            for f in files:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    task_status = data.get("status", "unknown")
                    if status and task_status != status:
                        continue

                    # Extract task_id from data or filename
                    task_id = data.get("task_id", f.stem)

                    results.append(TaskSummary(
                        task_id=task_id,
                        prompt=data.get("prompt", ""),
                        target_url=data.get("navigation_url"),
                        actual_url=data.get("actual_url"),
                        status=task_status,
                        total_iterations=data.get("total_iterations", 0),
                        total_actions=data.get("total_actions", 0),
                        execution_time=data.get("execution_time", 0),
                        pages_visited=len(data.get("unique_pages", [])),
                        website_type=data.get("website_type"),
                        created_at=data.get("timestamp"),
                    ))
                except Exception:
                    continue

        return results[offset:offset + limit]

    def _load_json_for_task(self, task_id: str) -> dict:
        """Try to find matching JSON result file for a task"""
        if not EXECUTION_RESULTS_DIR.exists():
            return {}

        # Try exact match patterns
        patterns = [
            f"task_{task_id}.json",
            f"{task_id}.json",
            f"*{task_id}*.json",
        ]
        for pattern in patterns:
            matches = list(EXECUTION_RESULTS_DIR.glob(pattern))
            if matches:
                try:
                    return json.loads(matches[0].read_text(encoding="utf-8"))
                except Exception:
                    continue

        # Search by task_id inside files
        for f in EXECUTION_RESULTS_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("task_id") == task_id:
                    return data
            except Exception:
                continue

        return {}


class LogService:
    """Log retrieval from DB and filesystem"""

    def get_task_logs(self, task_id: str) -> List[LogEntry]:
        session = get_session()
        try:
            logs = session.query(AutomationLog).filter_by(
                task_id=task_id
            ).order_by(AutomationLog.timestamp).all()

            return [
                LogEntry(
                    timestamp=log.timestamp.isoformat() if log.timestamp else None,
                    level=log.log_level or "INFO",
                    component=log.component or "",
                    message=log.message or "",
                )
                for log in logs
            ]
        finally:
            session.close()

    def get_recent_logs(self, lines: int = 200) -> List[LogEntry]:
        """Read the most recent log file"""
        if not LOGS_DIR.exists():
            return []

        log_files = sorted(LOGS_DIR.glob("automation_*.log"), reverse=True)
        if not log_files:
            return []

        entries = []
        try:
            with open(log_files[0], "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    entry = self._parse_log_line(line.strip())
                    if entry:
                        entries.append(entry)
        except Exception:
            pass

        return entries

    def get_latest_log_file(self) -> Optional[Path]:
        """Get path to the latest log file"""
        if not LOGS_DIR.exists():
            return None
        log_files = sorted(LOGS_DIR.glob("automation_*.log"), reverse=True)
        return log_files[0] if log_files else None

    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        if not line:
            return None
        # Format: "2026-04-18 23:35:25 - component - LEVEL - message"
        match = re.match(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*-\s*(\S+)\s*-\s*(\w+)\s*-\s*(.*)",
            line
        )
        if match:
            return LogEntry(
                timestamp=match.group(1),
                component=match.group(2),
                level=match.group(3),
                message=match.group(4),
            )
        return LogEntry(message=line)


class ScreenshotService:
    """Screenshot retrieval from filesystem"""

    def get_task_screenshots(self, task_id: str) -> List[ScreenshotInfo]:
        screenshots = []

        # Check task-specific subdirectory
        task_dir = SCREENSHOTS_DIR / task_id
        if task_dir.exists():
            for f in sorted(task_dir.glob("*.png")):
                screenshots.append(self._file_to_info(f, task_id))
        else:
            # Check root screenshots dir for step files matching this task
            if SCREENSHOTS_DIR.exists():
                for f in sorted(SCREENSHOTS_DIR.glob(f"*{task_id}*.png")):
                    screenshots.append(self._file_to_info(f, task_id))

                # Also check for step files with matching timestamp
                ts_prefix = task_id[:15]  # YYYYMMDD_HHMMSS
                for f in sorted(SCREENSHOTS_DIR.glob(f"step_*_{ts_prefix}*.png")):
                    screenshots.append(self._file_to_info(f, task_id))

        return screenshots

    def get_screenshot_path(self, task_id: str, filename: str) -> Optional[Path]:
        """Get absolute path for a screenshot file"""
        # Check task subdirectory
        path = SCREENSHOTS_DIR / task_id / filename
        if path.exists():
            return path

        # Check root
        path = SCREENSHOTS_DIR / filename
        if path.exists():
            return path

        return None

    def _file_to_info(self, f: Path, task_id: str) -> ScreenshotInfo:
        # Extract step number from filename like step_001_...
        step_match = re.search(r"step_(\d+)", f.name)
        step_num = int(step_match.group(1)) if step_match else None

        return ScreenshotInfo(
            filename=f.name,
            path=str(f),
            url=f"/api/v1/screenshots/{task_id}/{f.name}",
            size_bytes=f.stat().st_size,
            step_number=step_num,
        )


class SettingsService:
    """Read-only settings display"""

    def get_settings(self) -> SettingsResponse:
        from config.settings import settings
        return SettingsResponse(
            app_name=settings.app_name,
            app_version=settings.app_version,
            environment=settings.environment,
            browser_type=settings.browser_type,
            headless=settings.headless,
            window_width=settings.window_width,
            window_height=settings.window_height,
            anti_bot_enabled=settings.anti_bot_enabled,
            database_url=settings.database_url,
            log_level=settings.log_level,
            gemini_model=settings.gemini_model,
            computer_use_model=settings.computer_use_model,
            screenshots_enabled=settings.screenshots_enabled,
            max_retry_attempts=settings.max_retry_attempts,
        )
