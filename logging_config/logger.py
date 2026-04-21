"""
Logger Configuration
Structured logging for the application
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    return logging.getLogger(name)


def configure_logging():
    """Configure application logging"""
    
    # Create logs directory
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    
    # Configure sys.stdout to handle utf-8 if supported
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    # File handler
    log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    class SafeStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except UnicodeEncodeError:
                try:
                    # Fallback carefully replacing non-ASCII characters
                    msg = msg.encode('ascii', 'replace').decode('ascii')
                    stream.write(msg + self.terminator)
                    self.flush()
                except Exception:
                    self.handleError(record)
            except Exception:
                self.handleError(record)
                
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger