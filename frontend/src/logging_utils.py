"""
Moduł pomocniczy do importu systemu logowania z głównego projektu
"""
import sys
import os

# Znajdź ścieżkę do głównego katalogu projektu
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Usuń lokalny katalog frontend ze ścieżki, aby uniknąć konfliktu z lokalnym modułem config
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path_to_remove in ['', '.', current_dir]:
    while path_to_remove in sys.path:
        sys.path.remove(path_to_remove)

# Dodaj ścieżkę do głównego katalogu projektu na początku
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import funkcji logowania
from config.logging import init_logging, get_logger, debug, info, warning, error

__all__ = ['init_logging', 'get_logger', 'debug', 'info', 'warning', 'error']
