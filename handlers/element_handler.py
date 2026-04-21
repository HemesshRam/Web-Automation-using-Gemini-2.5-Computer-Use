"""
Element Handler
Handles all element interaction operations
"""

import logging
import time
from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import settings
from logging_config.logger import get_logger


logger = get_logger(__name__)


class ElementHandler:
    """Handle web element operations"""
    
    def __init__(self, driver):
        """Initialize element handler"""
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.element_wait_timeout)
    
    def find_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: Optional[int] = None):
        """Find element with wait"""
        try:
            timeout = timeout or settings.element_wait_timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"Element found: {selector}")
            return element
        
        except TimeoutException:
            logger.warning(f"Element not found: {selector}")
            return None
    
    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR) -> List:
        """Find multiple elements"""
        try:
            elements = self.driver.find_elements(by, selector)
            logger.info(f"Found {len(elements)} elements for selector: {selector}")
            return elements
        
        except NoSuchElementException:
            logger.warning(f"No elements found for selector: {selector}")
            return []
    
    def get_element_text(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[str]:
        """Get element text content"""
        try:
            element = self.find_element(selector, by)
            if element:
                text = element.text
                logger.info(f"Retrieved text from element: {text[:50]}...")
                return text
            return None
        
        except Exception as e:
            logger.error(f"Failed to get element text: {str(e)}")
            return None
    
    def get_element_attribute(self, selector: str, attribute: str, by: By = By.CSS_SELECTOR) -> Optional[str]:
        """Get element attribute value"""
        try:
            element = self.find_element(selector, by)
            if element:
                value = element.get_attribute(attribute)
                logger.info(f"Retrieved attribute '{attribute}': {value}")
                return value
            return None
        
        except Exception as e:
            logger.error(f"Failed to get element attribute: {str(e)}")
            return None
    
    def is_element_visible(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Check if element is visible"""
        try:
            element = WebDriverWait(self.driver, settings.element_wait_timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            logger.info(f"Element is visible: {selector}")
            return True
        
        except TimeoutException:
            logger.info(f"Element is not visible: {selector}")
            return False
    
    def is_element_clickable(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Check if element is clickable"""
        try:
            WebDriverWait(self.driver, settings.element_wait_timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            logger.info(f"Element is clickable: {selector}")
            return True
        
        except TimeoutException:
            logger.info(f"Element is not clickable: {selector}")
            return False