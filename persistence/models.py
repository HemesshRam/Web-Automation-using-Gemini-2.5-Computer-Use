"""
SQLAlchemy Models
Database table definitions for task tracking, execution history, and URL history
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text

from .database import Base


class TaskMetadata(Base):
    """Task execution metadata - one record per automation task"""
    __tablename__ = 'task_metadata'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), unique=True, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    target_url = Column(String(500))
    actual_url = Column(String(500))

    # Execution details
    status = Column(String(20), default="running")  # 'running', 'success', 'failed', 'timeout'
    total_iterations = Column(Integer, default=0)
    total_actions = Column(Integer, default=0)
    execution_time = Column(Float, default=0.0)  # Seconds

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Results
    pages_visited = Column(Integer, default=0)
    errors = Column(Text)  # JSON list of errors

    def __repr__(self):
        return f"<Task {self.task_id}: {self.status}>"


class ExecutionHistory(Base):
    """Detailed execution history - step by step actions"""
    __tablename__ = 'execution_history'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), nullable=False, index=True)
    iteration = Column(Integer)
    action_type = Column(String(50))  # 'click', 'type', 'navigate', 'scroll', etc.
    target = Column(String(200))
    success = Column(Boolean)
    error_message = Column(Text)
    screenshot_path = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<History {self.task_id} iteration {self.iteration}>"


class URLHistory(Base):
    """URLs visited during task execution"""
    __tablename__ = 'url_history'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    iteration = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<URL {self.url}>"


# Keep legacy models for backward compatibility
class AutomationTask(Base):
    """Legacy automation task model (backward compatibility)"""
    __tablename__ = "automation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, index=True)
    task_name = Column(String(200))
    target_url = Column(String(500))
    status = Column(String(50), default="PENDING")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_steps = Column(Integer, default=0)
    successful_steps = Column(Integer, default=0)
    failed_steps = Column(Integer, default=0)
    error_message = Column(Text)
    screenshots_count = Column(Integer, default=0)
    execution_time = Column(Float, default=0.0)
    task_metadata_json = Column(Text)  # Renamed to avoid conflict with table name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AutomationLog(Base):
    """Legacy automation log model (backward compatibility)"""
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), index=True)
    log_level = Column(String(20))
    message = Column(Text)
    component = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text)