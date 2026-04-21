"""
Form Handler
Handles form filling and submission
"""

import logging
import time
from typing import Dict, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from config.settings import settings
from logging_config.logger import get_logger
from .element_handler import ElementHandler


logger = get_logger(__name__)


class FormHandler:
    """Handle form operations"""
    
    def __init__(self, driver, element_handler: Optional[ElementHandler] = None):
        """Initialize form handler"""
        self.driver = driver
        self.element_handler = element_handler or ElementHandler(driver)
    
    def fill_form(self, form_data: Dict[str, Any]) -> bool:
        """Fill form with provided data"""
        try:
            logger.info(f"Filling form with {len(form_data)} fields")
            
            successful_fields = 0
            for field_name, field_value in form_data.items():
                if self.fill_form_field(field_name, field_value):
                    successful_fields += 1
                
                # Random delay between fields
                time.sleep(settings.action_delay_min)
            
            logger.info(f"Form filled: {successful_fields}/{len(form_data)} fields")
            return successful_fields == len(form_data)
        
        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False
    
    def fill_form_field(self, field_name: str, field_value: Any) -> bool:
        """Fill single form field"""
        try:
            # Try different selectors
            selectors = [
                f"[name='{field_name}']",
                f"[id='{field_name}']",
                f"input[name='{field_name}']",
                f"input[id='{field_name}']",
                f"textarea[name='{field_name}']",
                f"select[name='{field_name}']"
            ]
            
            for selector in selectors:
                if self.element_handler.find_element(selector):
                    element = self.element_handler.find_element(selector)
                    
                    if element:
                        tag_name = element.tag_name.lower()
                        
                        if tag_name == 'select':
                            select = Select(element)
                            select.select_by_value(str(field_value))
                        elif tag_name == 'textarea':
                            element.clear()
                            element.send_keys(str(field_value))
                        elif tag_name == 'input':
                            input_type = element.get_attribute('type')
                            if input_type == 'checkbox':
                                if field_value and not element.is_selected():
                                    element.click()
                            elif input_type == 'radio':
                                if field_value:
                                    element.click()
                            else:
                                element.clear()
                                element.send_keys(str(field_value))
                        
                        logger.info(f"Field '{field_name}' filled successfully")
                        return True
            
            logger.warning(f"Field '{field_name}' not found with any selector")
            return False
        
        except Exception as e:
            logger.error(f"Failed to fill field '{field_name}': {str(e)}")
            return False
    
    def submit_form(self, form_selector: str = "form") -> bool:
        """Submit form"""
        try:
            form = self.element_handler.find_element(form_selector)
            
            if form:
                # Try to find submit button
                submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
                if submit_button:
                    submit_button.click()
                else:
                    # Fallback to form submit
                    form.submit()
                
                logger.info("Form submitted successfully")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Form submission failed: {str(e)}")
            return False