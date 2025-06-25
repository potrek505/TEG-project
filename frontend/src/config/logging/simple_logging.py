"""
Prosty system logowania dla serwisu AI
"""
import logging
import sys
from pathlib import Path
from typing import Optional

# Globalne ustawienia
_is_configured = False
_log_level = logging.INFO

def init_logging(
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = False  # W kontenerze nie zapisujemy do pliku
) -> None:
    """
    Jednorazowa inicjalizacja systemu logowania dla serwisu AI.
    """
    global _is_configured, _log_level
    
    if _is_configured:
        return
    
    # Ustawienia poziomu
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    _log_level = level_map.get(log_level.upper(), logging.INFO)
    
    # Wyczyść istniejące handlery
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Ustawienia formatera
    formatter = logging.Formatter(
        '[AI] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    root_logger.setLevel(_log_level)
    
    # Handler konsoli (główny w kontenerze)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(_log_level)
        root_logger.addHandler(console_handler)
    
    # Wycisz zewnętrzne biblioteki
    for lib in ["requests", "urllib3", "werkzeug", "openai", "httpx", "langchain", "langgraph"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    _is_configured = True
    # Potwierdzenie inicjalizacji
    system_logger = logging.getLogger("ai.system")
    system_logger.info("AI logging system initialized")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Pobiera logger dla modułu.
    """
    if not _is_configured:
        init_logging()
    
    if name is None:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'unknown')
        else:
            name = 'unknown'
    
    # Dodaj prefix ai do nazwy loggera
    if not name.startswith('ai.'):
        name = f"ai.{name}"
    
    return logging.getLogger(name)
