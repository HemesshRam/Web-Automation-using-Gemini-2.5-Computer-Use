"""
Data Repository
High-level data access operations for task tracking and execution history
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from .database import get_session
from .models import TaskMetadata, ExecutionHistory, URLHistory, AutomationTask, AutomationLog


class TaskRepository:
    """Repository for task-related database operations"""

    def __init__(self):
        self.session: Session = None

    def _get_session(self):
        """Get or create session"""
        if self.session is None:
            self.session = get_session()
        return self.session

    def save_task(self, task_data: dict) -> str:
        """
        Save new task to database

        Args:
            task_data: {
                'task_id': str,
                'prompt': str,
                'target_url': str,
                'status': str,
                'total_iterations': int,
                'total_actions': int,
                'execution_time': float
            }

        Returns:
            task_id
        """
        session = self._get_session()

        task = TaskMetadata(
            task_id=task_data['task_id'],
            prompt=task_data.get('prompt', ''),
            target_url=task_data.get('target_url'),
            actual_url=task_data.get('actual_url'),
            status=task_data.get('status', 'running'),
            total_iterations=task_data.get('total_iterations', 0),
            total_actions=task_data.get('total_actions', 0),
            execution_time=task_data.get('execution_time', 0.0),
            pages_visited=task_data.get('pages_visited', 0),
            errors=json.dumps(task_data.get('errors', []))
        )

        session.add(task)
        session.commit()

        return task.task_id

    def update_task(self, task_id: str, updates: dict):
        """Update existing task"""
        session = self._get_session()

        task = session.query(TaskMetadata).filter_by(task_id=task_id).first()

        if task:
            for key, value in updates.items():
                if key == 'errors' and isinstance(value, list):
                    setattr(task, key, json.dumps(value))
                elif hasattr(task, key):
                    setattr(task, key, value)

            if 'status' in updates and updates['status'] in ['success', 'failed', 'timeout']:
                task.completed_at = datetime.utcnow()

            session.commit()

    def get_task(self, task_id: str) -> Optional[TaskMetadata]:
        """Get task by ID"""
        session = self._get_session()
        return session.query(TaskMetadata).filter_by(task_id=task_id).first()

    def get_all_tasks(self) -> List[TaskMetadata]:
        """Get all tasks"""
        session = self._get_session()
        return session.query(TaskMetadata).order_by(TaskMetadata.created_at.desc()).all()

    def get_tasks_by_status(self, status: str) -> List[TaskMetadata]:
        """Get tasks by status"""
        session = self._get_session()
        return session.query(TaskMetadata).filter_by(status=status).all()

    def get_task_history(self, task_id: str) -> List[ExecutionHistory]:
        """Get execution history for task"""
        session = self._get_session()
        return session.query(ExecutionHistory).filter_by(task_id=task_id).order_by(
            ExecutionHistory.timestamp
        ).all()

    def add_execution_step(self, execution_data: dict):
        """Add execution step to history"""
        session = self._get_session()

        step = ExecutionHistory(
            task_id=execution_data['task_id'],
            iteration=execution_data.get('iteration'),
            action_type=execution_data.get('action_type'),
            target=execution_data.get('target'),
            success=execution_data.get('success', False),
            error_message=execution_data.get('error_message'),
            screenshot_path=execution_data.get('screenshot_path')
        )

        session.add(step)
        session.commit()

    def add_url_visited(self, task_id: str, url: str, iteration: int):
        """Record URL visited"""
        session = self._get_session()

        url_record = URLHistory(
            task_id=task_id,
            url=url,
            iteration=iteration
        )

        session.add(url_record)
        session.commit()

    def get_task_stats(self, task_id: str) -> dict:
        """Get comprehensive task statistics"""
        task = self.get_task(task_id)

        if not task:
            return {}

        history = self.get_task_history(task_id)
        success_actions = sum(1 for h in history if h.success)
        failed_actions = sum(1 for h in history if not h.success)

        session = self._get_session()
        urls = session.query(URLHistory).filter_by(task_id=task_id).all()
        unique_urls = len(set(u.url for u in urls))

        return {
            'task_id': task_id,
            'prompt': task.prompt,
            'target_url': task.target_url,
            'actual_url': task.actual_url,
            'status': task.status,
            'total_time': task.execution_time,
            'total_iterations': task.total_iterations,
            'total_actions': task.total_actions,
            'successful_actions': success_actions,
            'failed_actions': failed_actions,
            'urls_visited': unique_urls,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }

    def close(self):
        """Close session"""
        if self.session:
            self.session.close()
            self.session = None


# Keep legacy Repository class for backward compatibility
class Repository:
    """Legacy repository for backward compatibility"""

    def __init__(self, session: Session = None):
        """Initialize repository"""
        self.session = session or get_session()

    def create_task(self, task_id: str, task_name: str, target_url: str) -> AutomationTask:
        """Create new automation task"""
        task = AutomationTask(
            task_id=task_id,
            task_name=task_name,
            target_url=target_url,
            status="PENDING"
        )
        self.session.add(task)
        self.session.commit()
        return task

    def get_task(self, task_id: str) -> Optional[AutomationTask]:
        """Get task by ID"""
        return self.session.query(AutomationTask).filter(
            AutomationTask.task_id == task_id
        ).first()

    def update_task_status(self, task_id: str, status: str, **kwargs):
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()

            if 'end_time' in kwargs:
                task.end_time = kwargs['end_time']
            if 'successful_steps' in kwargs:
                task.successful_steps = kwargs['successful_steps']
            if 'failed_steps' in kwargs:
                task.failed_steps = kwargs['failed_steps']
            if 'error_message' in kwargs:
                task.error_message = kwargs['error_message']
            if 'execution_time' in kwargs:
                task.execution_time = kwargs['execution_time']

            self.session.commit()

        return task

    def get_all_tasks(self) -> List[AutomationTask]:
        """Get all tasks"""
        return self.session.query(AutomationTask).all()

    def get_tasks_by_status(self, status: str) -> List[AutomationTask]:
        """Get tasks by status"""
        return self.session.query(AutomationTask).filter(
            AutomationTask.status == status
        ).all()

    def create_log(self, task_id: str, log_level: str, message: str, component: str = "",
                   details: Optional[dict] = None):
        """Create automation log"""
        log = AutomationLog(
            task_id=task_id,
            log_level=log_level,
            message=message,
            component=component,
            details=json.dumps(details) if details else None
        )
        self.session.add(log)
        self.session.commit()
        return log

    def get_task_logs(self, task_id: str) -> List[AutomationLog]:
        """Get logs for specific task"""
        return self.session.query(AutomationLog).filter(
            AutomationLog.task_id == task_id
        ).order_by(AutomationLog.timestamp).all()