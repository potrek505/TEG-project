"""
Wspólna konfiguracja logowania dla projektu TEG
"""
import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path

def setup_logging(service_name="teg-project", log_level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
    """
    Konfiguruje logowanie dla aplikacji z rotacją i lepszą strukturą
    
    Args:
        service_name (str): Nazwa serwisu (ai, backend, frontend, main)
        log_level: Poziom logowania (domyślnie: INFO)
        max_bytes (int): Maksymalny rozmiar pliku logów przed rotacją (domyślnie: 10MB)
        backup_count (int): Liczba plików zapasowych do zachowania (domyślnie: 5)
    """
    
    # Pobierz katalog główny projektu
    project_root = Path(__file__).parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Wyczyść istniejące handlery aby uniknąć duplikatów
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Utwórz formatery
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler konsoli z obsługą kolorów dla różnych poziomów
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    
    # Rotujący handler pliku dla indywidualnego serwisu
    service_log_file = log_dir / f"{service_name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        service_log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    
    # Połączony plik logów dla wszystkich serwisów
    combined_log_file = log_dir / "combined.log"
    combined_handler = logging.handlers.RotatingFileHandler(
        combined_log_file,
        maxBytes=max_bytes * 2,  # Większy rozmiar dla połączonego logu
        backupCount=backup_count,
        encoding='utf-8'
    )
    combined_handler.setFormatter(detailed_formatter)
    combined_handler.setLevel(log_level)
    
    # Plik logów tylko błędów dla wszystkich serwisów
    error_log_file = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Skonfiguruj root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(combined_handler)
    root_logger.addHandler(error_handler)
    
    # Ustaw loggery bibliotek zewnętrznych na WARNING aby zmniejszyć szum
    third_party_loggers = [
        "requests", "urllib3", "werkzeug", "langchain", "openai", 
        "httpx", "httpcore", "streamlit", "matplotlib", "PIL"
    ]
    
    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Utwórz logger specyficzny dla serwisu
    logger = logging.getLogger(service_name)
    logger.info(f"Logowanie skonfigurowane dla {service_name}")
    logger.info(f"Pliki logów: {service_log_file}, {combined_log_file}, {error_log_file}")
    
    return logger

def get_logger(name):
    """
    Pobiera instancję loggera dla konkretnego modułu/klasy
    
    Args:
        name (str): Nazwa loggera (zwykle __name__)
    
    Returns:
        logging.Logger: Skonfigurowana instancja loggera
    """
    return logging.getLogger(name)
