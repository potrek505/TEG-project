"""
Prosty menedżer konfiguracji dla serwisu Frontend.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class FrontendConfigManager:
    """Prosty menedżer konfiguracji dla Frontend."""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "frontend_config.json"
        self.env_file = Path(__file__).parent / ".env"
        self._config = {}
        self._watching = True
        
        # Wczytaj konfigurację
        self.reload_config()
        
        # Uruchom file watcher
        threading.Thread(target=self._watch_files, daemon=True).start()
    
    def reload_config(self):
        """Wczytaj konfigurację."""
        # Domyślna konfiguracja
        self._config = {
            "server": {
                "port": 8501,
                "debug": False
            },
            "app": {
                "title": "Your Finance Buddy",
                "layout": "wide",
                "theme": "light"
            },
            "backend_service": {
                "url": "http://backend:5000",
                "timeout": 30
            },
            "ui": {
                "sidebar_expanded": True,
                "show_logs": False,
                "max_messages": 50
            }
        }
        
        # Wczytaj z pliku JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._config.update(file_config)
            except Exception as e:
                print(f"Błąd wczytywania konfiguracji Frontend: {e}")
        
        # Wczytaj zmienne środowiskowe
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Nadpisz zmiennymi środowiskowymi
        if os.getenv("FRONTEND_PORT"):
            self._config["server"]["port"] = int(os.getenv("FRONTEND_PORT"))
        if os.getenv("FRONTEND_DEBUG"):
            self._config["server"]["debug"] = os.getenv("FRONTEND_DEBUG").lower() == "true"
        if os.getenv("BACKEND_SERVICE_URL"):
            self._config["backend_service"]["url"] = os.getenv("BACKEND_SERVICE_URL")
        if os.getenv("APP_TITLE"):
            self._config["app"]["title"] = os.getenv("APP_TITLE")
        if os.getenv("APP_THEME"):
            self._config["app"]["theme"] = os.getenv("APP_THEME")
        if os.getenv("SIDEBAR_EXPANDED"):
            self._config["ui"]["sidebar_expanded"] = os.getenv("SIDEBAR_EXPANDED").lower() == "true"
        if os.getenv("MAX_MESSAGES"):
            self._config["ui"]["max_messages"] = int(os.getenv("MAX_MESSAGES"))
    
    def get(self, *keys, default=None):
        """Pobierz wartość z konfiguracji."""
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, *args):
        """Ustaw wartość w konfiguracji."""
        if len(args) < 2:
            return False
        
        keys = args[:-1]
        value = args[-1]
        
        # Znajdź miejsce w konfiguracji
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        
        # Zapisz do pliku
        self.save_config()
        return True
    
    def save_config(self):
        """Zapisz konfigurację do pliku."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            print(f"Frontend config saved to {self.config_file}")
        except Exception as e:
            print(f"Błąd zapisywania konfiguracji Frontend: {e}")
    
    def _watch_files(self):
        """Obserwuj zmiany w plikach."""
        last_modified = {}
        files = [self.config_file, self.env_file]
        
        for file_path in files:
            if file_path.exists():
                last_modified[file_path] = file_path.stat().st_mtime
        
        while self._watching:
            try:
                for file_path in files:
                    if file_path.exists():
                        current_time = file_path.stat().st_mtime
                        if file_path not in last_modified or current_time > last_modified[file_path]:
                            last_modified[file_path] = current_time
                            print(f"Frontend config file changed: {file_path}")
                            self.reload_config()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error watching Frontend config files: {e}")
                time.sleep(5)
    
    def stop_watching(self):
        """Zatrzymaj obserwowanie plików."""
        self._watching = False

# Globalny instance
_frontend_config = None

def get_frontend_config():
    """Pobierz globalny config manager."""
    global _frontend_config
    if _frontend_config is None:
        _frontend_config = FrontendConfigManager()
    return _frontend_config
