"""
Header Manager
Manages HTTP headers to mimic real browsers
"""

import random
import logging
from typing import Dict
from logging_config.logger import get_logger


logger = get_logger(__name__)


class HeaderManager:
    """Manage HTTP headers"""
    
    CHROME_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="91", "Google Chrome";v="91"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }
    
    FIREFOX_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    }
    
    SAFARI_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    def __init__(self):
        """Initialize header manager"""
        self.headers_pool = [self.CHROME_HEADERS, self.FIREFOX_HEADERS, self.SAFARI_HEADERS]
    
    def get_random_headers(self) -> Dict[str, str]:
        """Get random headers"""
        headers = random.choice(self.headers_pool).copy()
        logger.debug(f"Selected headers profile")
        return headers
    
    def get_chrome_headers(self) -> Dict[str, str]:
        """Get Chrome headers"""
        return self.CHROME_HEADERS.copy()
    
    def get_firefox_headers(self) -> Dict[str, str]:
        """Get Firefox headers"""
        return self.FIREFOX_HEADERS.copy()
    
    def get_safari_headers(self) -> Dict[str, str]:
        """Get Safari headers"""
        return self.SAFARI_HEADERS.copy()