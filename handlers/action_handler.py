"""
Action Handler - Enhanced
Handles generic automation actions with anti-bot evasion
FIXED: Improved error handling and timeout management
"""

import logging
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)

from config.settings import settings
from logging_config.logger import get_logger
from .element_handler import ElementHandler
from detectors.anti_bot_service import AntiBotService


logger = get_logger(__name__)


class ActionHandler:
    """Handle automation actions with anti-bot evasion"""
    
    def __init__(self, driver, element_handler: Optional[ElementHandler] = None):
        """Initialize action handler"""
        self.driver = driver
        self.element_handler = element_handler or ElementHandler(driver)
        self.anti_bot = AntiBotService()
        self.wait = WebDriverWait(driver, settings.element_wait_timeout)
    
    def click_element(self, selector: str, by: By = By.CSS_SELECTOR, retries: int = 3) -> bool:
        """Click element with retry logic and anti-bot evasion"""
        for attempt in range(retries):
            try:
                element = self.element_handler.find_element(selector, by)
                
                if element:
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.3)
                    
                    # Check if clickable
                    self.wait.until(EC.element_to_be_clickable((by, selector)))
                    
                    # Click with action chains for natural interaction
                    ActionChains(self.driver).move_to_element(element).pause(0.2).click().perform()
                    
                    # Anti-bot delay
                    time.sleep(self.anti_bot.get_random_delay())
                    
                    logger.info(f"✓ Clicked: {selector}")
                    return True
                
                if attempt < retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{retries} for click: {selector}")
                    time.sleep(1.0)
            
            except StaleElementReferenceException:
                logger.warning(f"Stale element, retrying: {selector}")
                if attempt < retries - 1:
                    time.sleep(1.0)
            
            except TimeoutException:
                logger.warning(f"Element not clickable within timeout: {selector}")
                if attempt < retries - 1:
                    time.sleep(1.0)
            
            except Exception as e:
                logger.error(f"Click failed (attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(1.0)
        
        logger.error(f"✗ Failed to click after {retries} attempts: {selector}")
        return False
    
    def fill_input(self, selector: str, value: str, by: By = By.CSS_SELECTOR, retries: int = 3) -> bool:
        """Fill input field with realistic typing"""
        for attempt in range(retries):
            try:
                element = self.element_handler.find_element(selector, by)
                
                if element:
                    # Click to focus
                    element.click()
                    time.sleep(0.2)
                    
                    # Clear existing content
                    element.clear()
                    time.sleep(0.1)
                    
                    # Type with realistic delays (character by character)
                    for char in str(value):
                        element.send_keys(char)
                        # Add anti-bot typing delay
                        time.sleep(self.anti_bot.get_realistic_typing_delay())
                    
                    # Anti-bot delay after filling
                    time.sleep(self.anti_bot.get_random_delay())
                    
                    logger.info(f"✓ Filled input: {selector}")
                    return True
                
                if attempt < retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{retries} for fill: {selector}")
                    time.sleep(1.0)
            
            except StaleElementReferenceException:
                logger.warning(f"Stale element, retrying: {selector}")
                if attempt < retries - 1:
                    time.sleep(1.0)
            
            except Exception as e:
                logger.error(f"Fill input failed (attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(1.0)
        
        logger.error(f"✗ Failed to fill input after {retries} attempts: {selector}")
        return False
    
    def hover_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Hover over element with anti-bot evasion"""
        try:
            element = self.element_handler.find_element(selector, by)
            
            if element:
                # Move to element gradually
                ActionChains(self.driver).move_to_element(element).perform()
                time.sleep(self.anti_bot.get_random_delay())
                
                logger.info(f"✓ Hovered: {selector}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Hover failed: {str(e)}")
            return False
    
    def press_key(self, key, retries: int = 3) -> bool:
        """Press keyboard key"""
        for attempt in range(retries):
            try:
                ActionChains(self.driver).send_keys(key).perform()
                time.sleep(self.anti_bot.get_random_delay())
                
                logger.info(f"✓ Key pressed: {key}")
                return True
            
            except Exception as e:
                logger.error(f"Key press failed (attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(0.5)
        
        logger.error(f"✗ Failed to press key after {retries} attempts")
        return False
    
    def scroll_page(self, direction: str = "down", pixels: int = 500) -> bool:
        """Scroll page with anti-bot delays"""
        try:
            if direction.lower() == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction.lower() == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            else:
                logger.warning(f"Unknown scroll direction: {direction}")
                return False
            
            time.sleep(self.anti_bot.get_random_delay())
            
            logger.info(f"✓ Scrolled {direction} by {pixels}px")
            return True
        
        except Exception as e:
            logger.error(f"Scroll failed: {str(e)}")
            return False
    
    def get_page_source(self) -> Optional[str]:
        """Get page source HTML"""
        try:
            source = self.driver.page_source
            logger.info(f"✓ Page source retrieved ({len(source)} bytes)")
            return source
        
        except Exception as e:
            logger.error(f"Failed to get page source: {str(e)}")
            return None
    
    def take_screenshot(self, filepath: str) -> bool:
        """Take screenshot of current page"""
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"✓ Screenshot saved: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return False
    
    def wait_for_navigation(self, timeout: Optional[int] = None) -> bool:
        """Wait for page navigation to complete"""
        try:
            timeout = timeout or settings.page_load_timeout
            # Wait for document ready state
            self.wait.until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            logger.info(f"✓ Navigation completed")
            return True
        
        except TimeoutException:
            logger.warning(f"Navigation timeout after {timeout}s")
            return False
        
        except Exception as e:
            logger.error(f"Navigation wait failed: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            url = self.driver.current_url
            logger.info(f"Current URL: {url}")
            return url
        
        except Exception as e:
            logger.error(f"Failed to get URL: {str(e)}")
            return ""
    
    def switch_to_iframe(self, iframe_selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Switch to iframe context"""
        try:
            iframe = self.element_handler.find_element(iframe_selector, by)
            if iframe:
                self.driver.switch_to.frame(iframe)
                logger.info(f"✓ Switched to iframe: {iframe_selector}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Switch to iframe failed: {str(e)}")
            return False
    
    def switch_to_default_content(self) -> bool:
        """Switch back to default content"""
        try:
            self.driver.switch_to.default_content()
            logger.info(f"✓ Switched back to default content")
            return True
        
        except Exception as e:
            logger.error(f"Switch to default content failed: {str(e)}")
            return False