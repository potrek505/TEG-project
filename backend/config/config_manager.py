"""
Prosty menedżer konfiguracji dla serwisu Backend.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class BackendConfigManager:
    """Prosty menedżer konfiguracji dla Backend."""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "backend_config.json"
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
                "port": 5000,
                "debug": False
            },
            "ai_service": {
                "url": "http://ai:5001",
                "timeout": 60
            },
            "database": {
                "conversations_path": "./conversations.db"
            },
            "cors": {
                "enabled": True,
                "origins": ["*"]
            },
            "security": {
                "rate_limiting": True,
                "max_requests_per_minute": 100
            }
        }
        
        # Wczytaj z pliku JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._config.update(file_config)
            except Exception as e:
                print(f"Błąd wczytywania konfiguracji Backend: {e}")
        
        # Wczytaj zmienne środowiskowe
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Nadpisz zmiennymi środowiskowymi
        if os.getenv("BACKEND_PORT"):
            self._config["server"]["port"] = int(os.getenv("BACKEND_PORT"))
        if os.getenv("BACKEND_DEBUG"):
            self._config["server"]["debug"] = os.getenv("BACKEND_DEBUG").lower() == "true"
        if os.getenv("AI_SERVICE_URL"):
            self._config["ai_service"]["url"] = os.getenv("AI_SERVICE_URL")
        if os.getenv("CONVERSATIONS_DB_PATH"):
            self._config["database"]["conversations_path"] = os.getenv("CONVERSATIONS_DB_PATH")
        if os.getenv("CORS_ORIGINS"):
            origins = os.getenv("CORS_ORIGINS").split(",")
            self._config["cors"]["origins"] = [o.strip() for o in origins]
        if os.getenv("MAX_REQUESTS_PER_MINUTE"):
            self._config["security"]["max_requests_per_minute"] = int(os.getenv("MAX_REQUESTS_PER_MINUTE"))
    
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
            print(f"Backend config saved to {self.config_file}")
        except Exception as e:
            print(f"Błąd zapisywania konfiguracji Backend: {e}")
    
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
                            print(f"Backend config file changed: {file_path}")
                            self.reload_config()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error watching Backend config files: {e}")
                time.sleep(5)
    
    def stop_watching(self):
        """Zatrzymaj obserwowanie plików."""
        self._watching = False

# Globalny instance
_backend_config = None

def get_backend_config():
    """Pobierz globalny config manager."""
    global _backend_config
    if _backend_config is None:
        _backend_config = BackendConfigManager()
    return _backend_config
