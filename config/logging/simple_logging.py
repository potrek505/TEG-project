"""
Prosty system logowania dla projektu TEG
Zastępuje skomplikowany poprzedni system
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
    file_output: bool = True
) -> None:
    """
    Jednorazowa inicjalizacja systemu logowania dla całego projektu.
    
    Args:
        log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR)
        console_output: Czy wypisywać logi na konsolę
        file_output: Czy zapisywać logi do pliku
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
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    root_logger.setLevel(_log_level)
    
    # Handler konsoli
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(_log_level)
        root_logger.addHandler(console_handler)
    
    # Handler pliku (jeden plik dla całego projektu)
    if file_output:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "teg_app.log"  # Zmieniona nazwa
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(_log_level)
        root_logger.addHandler(file_handler)
    
    # Wycisz zewnętrzne biblioteki
    for lib in ["requests", "urllib3", "werkzeug", "openai", "httpx", "streamlit"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    _is_configured = True
    # Utwórz logger systemu do potwierdzenia inicjalizacji
    system_logger = logging.getLogger("system")
    system_logger.info("System logowania został zainicjalizowany")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Pobiera logger dla modułu.
    
    Args:
        name: Nazwa loggera (domyślnie __name__ z miejsca wywołania)
    
    Returns:
        Skonfigurowany logger
    """
    if not _is_configured:
        init_logging()
    
    if name is None:
        # Spróbuj automatycznie wykryć nazwę modułu
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'unknown')
        else:
            name = 'unknown'
    
    return logging.getLogger(name)

# Funkcje pomocnicze dla szybkiego użycia
def debug(msg: str, name: str = "app") -> None:
    """Szybkie logowanie DEBUG"""
    get_logger(name).debug(msg)

def info(msg: str, name: str = "app") -> None:
    """Szybkie logowanie INFO"""
    get_logger(name).info(msg)

def warning(msg: str, name: str = "app") -> None:
    """Szybkie logowanie WARNING"""
    get_logger(name).warning(msg)

def error(msg: str, name: str = "app") -> None:
    """Szybkie logowanie ERROR"""
    get_logger(name).error(msg)

def clear_logs() -> None:
    """Wyczyść plik logów"""
    project_root = Path(__file__).parent.parent.parent
    log_file = project_root / "logs" / "teg_app.log"
    
    if log_file.exists():
        log_file.unlink()
        print("Wyczyszczono plik logów")
    else:
        print("Plik logów nie istnieje")

def show_logs(lines: int = 50) -> None:
    """Pokaż ostatnie wpisy z logów"""
    project_root = Path(__file__).parent.parent.parent
    log_file = project_root / "logs" / "teg_app.log"
    
    if not log_file.exists():
        print("Plik logów nie istnieje")
        return
    
    import subprocess
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), str(log_file)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"Błąd przy odczycie logów: {e}")
