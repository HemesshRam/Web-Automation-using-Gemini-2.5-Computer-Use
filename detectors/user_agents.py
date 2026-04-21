"""
User Agent Rotator
Provides rotating user agents to avoid detection
"""

import random
import logging
from typing import List
from logging_config.logger import get_logger


logger = get_logger(__name__)


class UserAgentRotator:
    """Manage user agent rotation"""
    
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67",
        
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    ]
    
    def __init__(self):
        """Initialize user agent rotator"""
        self.current_index = 0
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        agent = random.choice(self.USER_AGENTS)
        logger.debug(f"Selected user agent: {agent[:60]}...")
        return agent
    
    def get_next_user_agent(self) -> str:
        """Get next user agent in sequence"""
        agent = self.USER_AGENTS[self.current_index % len(self.USER_AGENTS)]
        self.current_index += 1
        logger.debug(f"Selected user agent: {agent[:60]}...")
        return agent
    
    def add_custom_user_agent(self, user_agent: str):
        """Add custom user agent"""
        if user_agent not in self.USER_AGENTS:
            self.USER_AGENTS.append(user_agent)
            logger.info(f"Added custom user agent")