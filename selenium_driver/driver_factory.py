"""
Driver Factory
Creates and configures Selenium WebDriver instances
"""

import logging
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

from config.settings import settings
from logging_config.logger import get_logger
from detectors.anti_bot_service import AntiBotService


logger = get_logger(__name__)


class DriverFactory:
    """Factory for creating WebDriver instances"""
    
    def __init__(self):
        """Initialize driver factory"""
        self.anti_bot_service = AntiBotService()
    
    def create_driver(self, browser_type: str = "chrome"):
        """Create WebDriver instance"""
        browser_type = browser_type.lower()
        
        if browser_type == "chrome":
            return self._create_chrome_driver()
        elif browser_type == "firefox":
            return self._create_firefox_driver()
        elif browser_type == "edge":
            return self._create_edge_driver()
        else:
            logger.error(f"Unsupported browser type: {browser_type}")
            return self._create_chrome_driver()
    
    def _create_chrome_driver(self):
        """Create Chrome WebDriver with visible browser support"""
        executable_path = None
        try:
            options = ChromeOptions()
            
            # HEADLESS MODE SETTING
            if settings.headless:
                options.add_argument('--headless=new')
                print(f"[BROWSER] Running in HEADLESS mode")
            else:
                print(f"[BROWSER] Running in VISIBLE mode (browser window will open)")
            
            # CRITICAL: Anti-automation detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Performance options
            if settings.disable_gpu:
                options.add_argument('--disable-gpu')
            
            if settings.no_sandbox:
                options.add_argument('--no-sandbox')
            
            if settings.disable_dev_shm:
                options.add_argument('--disable-dev-shm-usage')
            
            # Browser behavior options
            options.add_argument(f'--user-agent={self.anti_bot_service.get_random_user_agent()}')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            # NOTE: Images MUST be enabled for Computer Use (model sees screenshots)
            # options.add_argument('--disable-images')  # DISABLED - breaks Computer Use
            options.add_argument('--disable-java')
            options.add_argument('--disable-sync')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            
            # WebGL and performance
            options.add_argument('--enable-webgl')
            options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
            
            # Prefs for Chrome
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0,
                # NOTE: Images MUST load for Computer Use screenshots
                # "profile.managed_default_content_settings.images": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            # IMPORTANT: Handle Chrome executable path
            executable_path = settings.chrome_executable_path
            
            if executable_path:
                # Use custom Chrome browser binary
                from pathlib import Path
                chrome_path = Path(executable_path)
                
                if not chrome_path.exists():
                    logger.warning(f"Chrome executable not found at: {executable_path}")
                    logger.warning(f"Attempting to use system Chrome...")
                else:
                    logger.info(f"Using Chrome executable: {executable_path}")
                    options.binary_location = str(chrome_path)
            else:
                # Use system Chrome
                logger.info(f"Using system Chrome installation")
            
            options.page_load_strategy = 'eager'  # DOM-interactive is enough; screenshots wait separately
            driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(settings.page_load_timeout)
            driver.set_script_timeout(settings.page_load_timeout)
            driver.implicitly_wait(2)  # Reduced: explicit waits handle real timeouts
            
            logger.info(f"Chrome driver created successfully")
            logger.info(f"Headless: {settings.headless}")
            logger.info(f"Window size: 1920x1080")
            
            return driver
        
        except FileNotFoundError as e:
            logger.error(f"Chrome executable not found: {str(e)}")
            logger.info(f"Make sure CHROME_EXECUTABLE_PATH is correct in .env")
            raise
        
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {str(e)}")
            logger.error(f"Chrome path used: {executable_path if executable_path else 'system default'}")
            raise
    
    def _create_firefox_driver(self):
        """Create Firefox WebDriver"""
        try:
            options = FirefoxOptions()
            
            if settings.headless:
                options.add_argument('--headless')
            
            options.add_argument(f'user-agent={self.anti_bot_service.get_random_user_agent()}')
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')
            
            # Use custom executable path if provided
            if settings.firefox_executable_path:
                from pathlib import Path
                ff_path = Path(settings.firefox_executable_path)
                if ff_path.exists():
                    options.binary_location = str(ff_path)
                    logger.info(f"Using Firefox executable: {ff_path}")
                else:
                    logger.warning(f"Firefox executable not found at: {ff_path}")
            
            driver = webdriver.Firefox(options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(settings.page_load_timeout)
            driver.set_script_timeout(settings.page_load_timeout)
            
            logger.info("Firefox driver created successfully")
            return driver
        
        except Exception as e:
            logger.error(f"Failed to create Firefox driver: {str(e)}")
            raise
    
    def _create_edge_driver(self):
        """Create Edge WebDriver"""
        try:
            options = EdgeOptions()
            
            if settings.headless:
                options.add_argument('--headless')
            
            options.add_argument(f'--user-agent={self.anti_bot_service.get_random_user_agent()}')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Edge(options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(settings.page_load_timeout)
            driver.set_script_timeout(settings.page_load_timeout)
            
            logger.info("Edge driver created successfully")
            return driver
        
        except Exception as e:
            logger.error(f"Failed to create Edge driver: {str(e)}")
            raise