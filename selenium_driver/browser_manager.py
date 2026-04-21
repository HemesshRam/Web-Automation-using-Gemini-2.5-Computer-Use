"""
Browser Manager
Manages browser lifecycle and operations
"""

import logging
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import settings
from logging_config.logger import get_logger


logger = get_logger(__name__)


class BrowserManager:
    """Manage browser operations"""
    
    def __init__(self, driver):
        """Initialize browser manager"""
        self.driver = driver
    
    def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(1)  # Wait for page load
            logger.info("Navigation successful")
            return True
        
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
    
    def take_screenshot(self, filename: str) -> bool:
        """Take screenshot"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return False
    
    def close_browser(self):
        """Close browser"""
        try:
            self.driver.quit()
            logger.info("Browser closed successfully")
        
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def accept_alert(self) -> bool:
        """Accept JavaScript alert"""
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert.accept()
            logger.info("Alert accepted")
            return True
        
        except Exception as e:
            logger.error(f"Failed to accept alert: {str(e)}")
            return False
    
    def dismiss_alert(self) -> bool:
        """Dismiss JavaScript alert"""
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert.dismiss()
            logger.info("Alert dismissed")
            return True
        
        except Exception as e:
            logger.error(f"Failed to dismiss alert: {str(e)}")
            return False