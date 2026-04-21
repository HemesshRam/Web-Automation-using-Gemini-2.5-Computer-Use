"""
Base Workflow
Abstract base class for all workflows
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging

from logging_config.logger import get_logger


logger = get_logger(__name__)


class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, workflow_name: str):
        """Initialize workflow"""
        self.workflow_name = workflow_name
        self.start_time = None
        self.end_time = None
        self.execution_results = []
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute workflow"""
        pass
    
    def get_execution_time(self) -> float:
        """Get execution time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def log_result(self, status: str, message: str, data: Dict[str, Any] = None):
        """Log workflow result"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message,
            'data': data or {}
        }
        self.execution_results.append(result)
        self.logger.info(f"{status}: {message}")
    
    def get_results(self) -> Dict[str, Any]:
        """Get workflow results"""
        return {
            'workflow_name': self.workflow_name,
            'execution_time': self.get_execution_time(),
            'results': self.execution_results
        }