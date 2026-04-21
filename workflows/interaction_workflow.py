"""
Interaction Workflow
Workflow for complex interactions
"""

from typing import Dict, List, Any
from datetime import datetime

from .base_workflow import BaseWorkflow
from core.action_executor import ActionExecutor


class InteractionWorkflow(BaseWorkflow):
    """Workflow for complex interaction operations"""
    
    def __init__(self, driver, actions: List[Dict[str, Any]]):
        """Initialize interaction workflow"""
        super().__init__("InteractionWorkflow")
        self.driver = driver
        self.actions = actions
        self.action_executor = ActionExecutor(driver)
    
    def execute(self) -> Dict[str, Any]:
        """Execute interaction workflow"""
        self.start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting interaction workflow with {len(self.actions)} actions")
            
            successful = 0
            for action in self.actions:
                if self.execute_action(action):
                    successful += 1
            
            self.log_result("SUCCESS", f"Executed {successful}/{len(self.actions)} actions")
            
        except Exception as e:
            self.logger.error(f"Interaction workflow failed: {str(e)}")
            self.log_result("FAILED", f"Interaction failed: {str(e)}")
        
        finally:
            self.end_time = datetime.now()
        
        return self.get_results()
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute single action"""
        try:
            action_type = action.get('type')
            
            if action_type == 'click':
                return self.action_executor.click_element(action.get('selector'))
            elif action_type == 'fill':
                return self.action_executor.fill_input(
                    action.get('selector'),
                    action.get('value')
                )
            elif action_type == 'hover':
                return self.action_executor.hover_element(action.get('selector'))
            
            return False
        
        except Exception as e:
            self.logger.error(f"Action execution failed: {str(e)}")
            return False