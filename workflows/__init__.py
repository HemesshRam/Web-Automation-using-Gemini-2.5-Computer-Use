"""
Workflows Package
Automation workflow classes and patterns
"""

from .base_workflow import BaseWorkflow
from .form_filling_workflow import FormFillingWorkflow
from .scraping_workflow import ScrapingWorkflow
from .interaction_workflow import InteractionWorkflow

__all__ = [
    'BaseWorkflow',
    'FormFillingWorkflow',
    'ScrapingWorkflow',
    'InteractionWorkflow'
]