"""
Test Anti-Bot Service
Unit tests for anti-bot detection bypass
"""

import pytest
from detectors.anti_bot_service import AntiBotService
from detectors.user_agents import UserAgentRotator
from detectors.headers import HeaderManager


class TestAntiBotService:
    """Test cases for anti-bot service"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        service = AntiBotService()
        assert service.user_agent_rotator is not None
        assert service.header_manager is not None
    
    def test_random_delay(self):
        """Test random delay generation"""
        service = AntiBotService()
        delay = service.get_random_delay()
        assert 1.0 <= delay <= 5.0
    
    def test_typing_delay(self):
        """Test typing delay"""
        service = AntiBotService()
        delay = service.get_realistic_typing_delay()
        assert 0.05 <= delay <= 0.15
    
    def test_user_agent_rotation(self):
        """Test user agent rotation"""
        rotator = UserAgentRotator()
        ua1 = rotator.get_random_user_agent()
        ua2 = rotator.get_next_user_agent()
        
        assert ua1 is not None
        assert ua2 is not None
        assert len(ua1) > 0
        assert len(ua2) > 0
    
    def test_header_manager(self):
        """Test header manager"""
        manager = HeaderManager()
        headers = manager.get_random_headers()
        
        assert headers is not None
        assert isinstance(headers, dict)
        assert 'Accept' in headers