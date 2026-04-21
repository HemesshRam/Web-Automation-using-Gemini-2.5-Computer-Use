"""
Pytest Configuration and Fixtures
Common fixtures for all tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from logging_config.logger import configure_logging, get_logger


@pytest.fixture(scope="session")
def setup_logging():
    """Setup logging for tests"""
    configure_logging()
    return get_logger(__name__)


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings"""
    return settings


@pytest.fixture
def mock_driver():
    """Create mock WebDriver"""
    return MagicMock()


@pytest.fixture
def mock_element():
    """Create mock WebElement"""
    element = MagicMock()
    element.text = "Test Text"
    element.tag_name = "input"
    element.get_attribute.return_value = "test_value"
    return element


@pytest.fixture
def temp_screenshot_dir(tmp_path):
    """Create temporary screenshot directory"""
    screenshot_dir = tmp_path / "screenshots"
    screenshot_dir.mkdir()
    return screenshot_dir


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary log directory"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir