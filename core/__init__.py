"""
Core Automation Package
Main automation engine and action execution
"""

from .automation_engine import AutomationEngine
from .action_executor import ActionExecutor

__all__ = ['AutomationEngine', 'ActionExecutor']