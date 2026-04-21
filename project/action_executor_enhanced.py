"""
Enhanced Action Executor - PRODUCTION READY
Executes automation actions with anti-bot evasion and guaranteed click success
Implements 3-method cascade: Selenium > ActionChains > JavaScript Force Click
"""

import time
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException
)

try:
    from config.settings import settings
except ImportError:
    settings = None

try:
    from logging_config.logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class ActionExecutor:
    """Execute automation actions with anti-bot evasion and indestructible clicks"""
    
    def __init__(self, driver, anti_bot_service=None):
        """Initialize action executor"""
        self.driver = driver
        self.anti_bot_service = anti_bot_service
        
        timeout = 15
        if settings and hasattr(settings, 'element_wait_timeout'):
            timeout = settings.element_wait_timeout
        
        self.wait = WebDriverWait(driver, timeout)
    
    def click_element_indestructible(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Indestructible Click - Tries 3 different click methods
        Method 1: Standard Selenium Click
        Method 2: ActionChains 
        Method 3: JavaScript Force Click
        """
        method_errors = {"m1": None, "m2": None, "m3": None}
        
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # METHOD 1: Standard Selenium Click
            try:
                self.wait.until(EC.element_to_be_clickable((by, selector))).click()
                logger.info(f"✓ Standard click succeeded: {selector}")
                self._post_click_delay()
                return True
            except Exception as error:
                method_errors["m1"] = str(error)
                logger.debug(f"[CLICK-M1] Standard click failed: {error}")
            
            # METHOD 2: ActionChains Move + Click
            try:
                ActionChains(self.driver).move_to_element(element).pause(0.2).click().perform()
                logger.info(f"✓ ActionChains click succeeded: {selector}")
                self._post_click_delay()
                return True
            except Exception as error:
                method_errors["m2"] = str(error)
                logger.debug(f"[CLICK-M2] ActionChains click failed: {error}")
            
            # METHOD 3: JavaScript Force Click
            try:
                self.driver.execute_script("""
                    document.querySelectorAll('[class*="overlay"], [class*="modal-backdrop"], [class*="popup"]').forEach(el => {
                        el.style.display = 'none';
                    });
                """)
                time.sleep(0.2)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"✓ JavaScript force click succeeded: {selector}")
                self._post_click_delay()
                return True
            except Exception as error:
                method_errors["m3"] = str(error)
                logger.error(f"✗ All click methods failed for {selector}")
                logger.error(f"  M1: {method_errors['m1'][:50] if method_errors['m1'] else 'N/A'}")
                logger.error(f"  M2: {method_errors['m2'][:50] if method_errors['m2'] else 'N/A'}")
                logger.error(f"  M3: {method_errors['m3'][:50] if method_errors['m3'] else 'N/A'}")
                return False
        
        except TimeoutException:
            logger.warning(f"✗ Element not found (timeout): {selector}")
            return False
        except Exception as error:
            logger.error(f"✗ Click failed unexpectedly {selector}: {str(error)}")
            return False
    
    def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Standard click element with human-like behavior"""
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, selector)))
            
            if self.anti_bot_service:
                delay = self.anti_bot_service.get_random_delay()
                time.sleep(delay)
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            
            ActionChains(self.driver).move_to_element(element).click().perform()
            
            if self.anti_bot_service:
                time.sleep(self.anti_bot_service.get_random_delay())
            
            logger.info(f"✓ Clicked: {selector}")
            return True
        
        except TimeoutException:
            logger.warning(f"✗ Element not clickable: {selector}")
            return self.click_element_indestructible(selector, by)
        except Exception as error:
            logger.error(f"✗ Click failed {selector}: {str(error)}")
            return self.click_element_indestructible(selector, by)
    
    def fill_input(self, selector: str, value: str, by: By = By.CSS_SELECTOR, clear_first: bool = True) -> bool:
        """Fill input field with realistic typing"""
        try:
            if not value:
                return False
            
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.2)
            
            element.click()
            time.sleep(0.1)
            
            if clear_first:
                element.clear()
                time.sleep(0.1)
            
            for char in value:
                element.send_keys(char)
                if self.anti_bot_service:
                    time.sleep(self.anti_bot_service.get_realistic_typing_delay())
                else:
                    time.sleep(0.05)
            
            logger.info(f"✓ Filled input: {selector}")
            return True
        
        except TimeoutException:
            logger.warning(f"✗ Input not found: {selector}")
            return False
        except Exception as error:
            logger.error(f"✗ Fill failed {selector}: {str(error)}")
            return False
    
    def select_dropdown(self, selector: str, value: str, by: By = By.CSS_SELECTOR) -> bool:
        """Select option from dropdown"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            select = Select(element)
            
            try:
                select.select_by_value(value)
            except:
                select.select_by_visible_text(value)
            
            if self.anti_bot_service:
                time.sleep(self.anti_bot_service.get_random_delay())
            
            logger.info(f"✓ Selected: {value}")
            return True
        
        except Exception as error:
            logger.error(f"✗ Select failed: {str(error)}")
            return False
    
    def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """Scroll page in specified direction"""
        try:
            for i in range(amount):
                if direction.lower() == "down":
                    self.driver.execute_script("window.scrollBy(0, 300);")
                elif direction.lower() == "up":
                    self.driver.execute_script("window.scrollBy(0, -300);")
                
                if self.anti_bot_service:
                    time.sleep(self.anti_bot_service.get_random_delay())
                else:
                    time.sleep(0.5)
            
            logger.info(f"✓ Scrolled {direction} ({amount}x)")
            return True
        
        except Exception as error:
            logger.error(f"✗ Scroll failed: {str(error)}")
            return False
    
    def send_keys(self, selector: str, keys: str, by: By = By.CSS_SELECTOR) -> bool:
        """Send keyboard keys to element"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            element.send_keys(keys)
            
            if self.anti_bot_service:
                time.sleep(self.anti_bot_service.get_random_delay())
            
            logger.info(f"✓ Sent keys to: {selector}")
            return True
        
        except Exception as error:
            logger.error(f"✗ Send keys failed: {str(error)}")
            return False
    
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: Optional[int] = None) -> bool:
        """Wait for element to be present"""
        try:
            timeout = timeout or 15
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
            logger.info(f"✓ Element found: {selector}")
            return True
        
        except TimeoutException:
            logger.warning(f"✗ Element not found: {selector}")
            return False
    
    def execute_javascript(self, script: str) -> Any:
        """Execute JavaScript code"""
        try:
            result = self.driver.execute_script(script)
            logger.info(f"✓ JavaScript executed")
            return result
        except Exception as error:
            logger.error(f"✗ JavaScript failed: {str(error)}")
            return None
    
    def drag_and_drop(self, source_selector: str, target_selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Perform drag and drop"""
        try:
            source = self.wait.until(EC.presence_of_element_located((by, source_selector)))
            target = self.wait.until(EC.presence_of_element_located((by, target_selector)))
            
            if self.anti_bot_service:
                time.sleep(self.anti_bot_service.get_random_delay())
            
            ActionChains(self.driver).drag_and_drop(source, target).perform()
            
            if self.anti_bot_service:
                time.sleep(self.anti_bot_service.get_random_delay())
            
            logger.info(f"✓ Drag and drop completed")
            return True
        
        except Exception as error:
            logger.error(f"✗ Drag and drop failed: {str(error)}")
            return False
    
    def navigate(self, url: str) -> bool:
        """Navigate to URL with dynamic waiting"""
        try:
            if not url or not url.startswith(('http://', 'https://')):
                if not url.startswith('www'):
                    return False
            
            self.driver.get(url)
            
            try:
                self._wait_for_network_idle(timeout=10)
            except:
                time.sleep(2)
            
            logger.info(f"✓ Navigated to: {url}")
            return True
        
        except Exception as error:
            logger.error(f"✗ Navigation failed: {str(error)}")
            return False
    
    def _wait_for_network_idle(self, timeout: int = 10):
        """Wait for network to be idle"""
        try:
            js_check = """
return (document.readyState === 'complete') &&
(typeof jQuery === 'undefined' || jQuery.active === 0);
"""
            WebDriverWait(self.driver, timeout).until(lambda d: d.execute_script(js_check))
            logger.debug("[NETWORK] Network idle - page fully loaded")
        except Exception as error:
            logger.debug(f"[NETWORK] Network wait timeout: {error}")
            time.sleep(1)
    
    def _post_click_delay(self):
        """Add human-like delay after click"""
        if self.anti_bot_service:
            time.sleep(self.anti_bot_service.get_random_delay())
        else:
            time.sleep(0.3)