"""
Anti-Bot Service
Implements anti-detection and anti-bot bypass measures
"""

import random
import time
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By

from config.settings import settings
from logging_config.logger import get_logger
from .user_agents import UserAgentRotator
from .headers import HeaderManager


logger = get_logger(__name__)


class AntiBotService:
    """Service for bypassing anti-bot detection"""
    
    def __init__(self):
        """Initialize anti-bot service"""
        self.user_agent_rotator = UserAgentRotator()
        self.header_manager = HeaderManager()
        logger.info("AntiBotService initialized")
    
    def apply_stealth_measures(self) -> Dict:
        """Apply stealth measures to bypass detection"""
        measures = {
            'user_agent': self.get_random_user_agent(),
            'headers': self.header_manager.get_random_headers(),
            'javascript_enabled': True,
            'cookies_enabled': True,
            'webgl_enabled': True
        }
        
        logger.info(f"Applied stealth measures: {measures.keys()}")
        return measures
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return self.user_agent_rotator.get_random_user_agent()
    
    def get_random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None) -> float:
        """Get random delay to mimic human behavior"""
        min_delay = min_delay or settings.delay_range_min
        max_delay = max_delay or settings.delay_range_max
        
        delay = random.uniform(min_delay, max_delay)
        return delay
    
    def get_realistic_typing_delay(self) -> float:
        """Get realistic typing delay between keystrokes"""
        return random.uniform(0.05, 0.15)
    
    def inject_anti_detection_scripts(self, driver) -> bool:
        """Inject JavaScript to hide automation - WORKS WITH VISIBLE BROWSERS"""
        try:
            # Remove headless indicators
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """)
            
            # Hide Chrome automation flags
            driver.execute_script("""
                window.chrome = {
                    runtime: {}
                };
            """)
            
            # Randomize plugin array
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', description: 'Portable Document Format'},
                        {name: 'Chrome PDF Viewer', description: 'Portable Document Format'},
                        {name: 'Native Client Executable', description: 'Native Client Executable'}
                    ],
                });
            """)
            
            # Override permissions
            driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
            """)
            
            # Randomize screen dimensions
            driver.execute_script("""
                Object.defineProperty(screen, 'width', {
                    get: () => 1920
                });
                Object.defineProperty(screen, 'height', {
                    get: () => 1080
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1040
                });
            """)
            
            # Override navigator.languages
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # Override navigator.platform
            driver.execute_script("""
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
            """)
            
            # Mask timezone
            driver.execute_script("""
                Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                    return {
                        locale: 'en-US',
                        calendar: 'gregory',
                        timeZone: 'America/New_York',
                        numberingSystem: 'latn',
                        hour12: true
                    };
                };
            """)
            
            # Override toString for Function
            driver.execute_script("""
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return originalToString.call(this);
                };
            """)
            
            logger.info("Anti-detection scripts injected successfully")
            return True
        
        except Exception as e:
            logger.warning(f"Failed to inject anti-detection scripts: {str(e)}")
            return False
    
    def get_stealth_options(self) -> Dict:
        """Get stealth mode options for browser launch"""
        return {
            'headless': settings.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-background-networking',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--disable-background-timer-throttling',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-preconnect',
                '--disable-sync',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-default-browser-check',
                '--safebrowsing-disable-auto-update',
                f'--user-agent={self.get_random_user_agent()}',
            ]
        }
    
    def rotate_user_agent(self) -> str:
        """Rotate user agent for each request"""
        new_agent = self.get_random_user_agent()
        logger.info(f"Rotated user agent: {new_agent[:50]}...")
        return new_agent