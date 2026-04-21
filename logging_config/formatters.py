"""
Log Formatters
Custom formatting for structured logging
"""

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Format logs as JSON"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class DetailedFormatter(logging.Formatter):
    """Detailed log formatter with colors"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format message
        formatted = super().format(record)
        
        # Reset levelname after formatting
        record.levelname = levelname
        
        return formatted


class SimpleFormatter(logging.Formatter):
    """Simple formatter"""
    
    def format(self, record):
        """Format log record simply"""
        return f"[{record.levelname}] {record.name} - {record.getMessage()}"


class VerboseFormatter(logging.Formatter):
    """Verbose formatter with all details"""
    
    def format(self, record):
        """Format log record verbosely"""
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
        else:
            exc_text = ""
        
        message = (
            f"{timestamp} | "
            f"{record.levelname:8} | "
            f"{record.name:30} | "
            f"{record.funcName}:{record.lineno:4} | "
            f"{record.getMessage()}"
        )
        
        if exc_text:
            message += f"\n{exc_text}"
        
        return message