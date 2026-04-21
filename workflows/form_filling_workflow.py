"""
Form Filling Workflow
Workflow for automated form filling
"""

from typing import Dict, Any
from datetime import datetime

from .base_workflow import BaseWorkflow
from handlers.form_handler import FormHandler


class FormFillingWorkflow(BaseWorkflow):
    """Workflow for form filling operations"""
    
    def __init__(self, driver, form_data: Dict[str, Any]):
        """Initialize form filling workflow"""
        super().__init__("FormFillingWorkflow")
        self.driver = driver
        self.form_data = form_data
        self.form_handler = FormHandler(driver)
    
    def execute(self) -> Dict[str, Any]:
        """Execute form filling workflow"""
        self.start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting form filling workflow with {len(self.form_data)} fields")
            
            # Fill form
            success = self.form_handler.fill_form(self.form_data)
            
            if success:
                self.log_result("SUCCESS", "Form filled successfully")
            else:
                self.log_result("PARTIAL", "Form filling completed with some failures")
            
        except Exception as e:
            self.logger.error(f"Form filling workflow failed: {str(e)}")
            self.log_result("FAILED", f"Form filling failed: {str(e)}")
        
        finally:
            self.end_time = datetime.now()
        
        return self.get_results()