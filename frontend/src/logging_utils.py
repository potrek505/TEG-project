"""
Moduł pomocniczy do logowania dla frontend
"""
import sys
import os

# Import lokalnego systemu logowania
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging import init_logging, get_logger, debug, info, warning, error

# Inicjalizuj system logowania
init_logging()

__all__ = ['init_logging', 'get_logger', 'debug', 'info', 'warning', 'error']
