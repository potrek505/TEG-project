"""
Prosty system logowania dla serwisu Frontend.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

class FrontendLogger:
    """Prosty logger dla Frontend."""
    
    def __init__(self):
        self.logger_name = "frontend"
        self.setup_logging()
    
    def setup_logging(self):
        """Konfiguracja systemu logowania."""
        # Konfiguruj główny logger
        logging.basicConfig(
            level=logging.INFO,
            format='[FRONTEND] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            stream=sys.stdout
        )
        
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Frontend logging system initialized")
    
    def get_logger(self, name=None):
        """Pobierz logger o podanej nazwie."""
        if name:
            return logging.getLogger(f"{self.logger_name}.{name}")
        return self.logger
    
    def debug(self, message, name=None):
        """Log debug message."""
        logger = self.get_logger(name)
        logger.debug(message)
    
    def info(self, message, name=None):
        """Log info message."""
        logger = self.get_logger(name)
        logger.info(message)
    
    def warning(self, message, name=None):
        """Log warning message."""
        logger = self.get_logger(name)
        logger.warning(message)
    
    def error(self, message, name=None):
        """Log error message."""
        logger = self.get_logger(name)
        logger.error(message)

# Globalny instance
_frontend_logger = None

def init_logging():
    """Inicjalizuj system logowania."""
    global _frontend_logger
    if _frontend_logger is None:
        _frontend_logger = FrontendLogger()
    return _frontend_logger

def get_logger(name=None):
    """Pobierz logger."""
    if _frontend_logger is None:
        init_logging()
    return _frontend_logger.get_logger(name)

def debug(message, name=None):
    """Log debug message."""
    if _frontend_logger is None:
        init_logging()
    _frontend_logger.debug(message, name)

def info(message, name=None):
    """Log info message."""
    if _frontend_logger is None:
        init_logging()
    _frontend_logger.info(message, name)

def warning(message, name=None):
    """Log warning message."""
    if _frontend_logger is None:
        init_logging()
    _frontend_logger.warning(message, name)

def error(message, name=None):
    """Log error message."""
    if _frontend_logger is None:
        init_logging()
    _frontend_logger.error(message, name)
