# Logging Configuration Package
# Centralna konfiguracja logowania dla projektu TEG

from .shared_logging import setup_logging, get_logger

__all__ = ['setup_logging', 'get_logger']
