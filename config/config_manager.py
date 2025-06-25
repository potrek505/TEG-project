"""
Prosty menedżer konfiguracji dla głównego projektu TEG.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class ProjectConfigManager:
    """Prosty menedżer konfiguracji dla głównego projektu."""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "project_config.json"
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
            "project": {
                "name": "TEG - Transaction Explorer with GraphRAG",
                "version": "1.0.0",
                "environment": "development"
            },
            "services": {
                "ai": {
                    "port": 5001,
                    "startup_delay": 3,
                    "health_check_interval": 30
                },
                "backend": {
                    "port": 5000,
                    "startup_delay": 2,
                    "health_check_interval": 30
                },
                "frontend": {
                    "port": 8501,
                    "startup_delay": 2,
                    "health_check_interval": 30
                }
            },
            "urls": {
                "ai_service": "http://localhost:5001",
                "backend_service": "http://localhost:5000",
                "frontend_url": "http://localhost:8501"
            },
            "database": {
                "transactions_db": "all_transactions.db",
                "transactions_db_uri": "sqlite:///all_transactions.db"
            },
            "deployment": {
                "use_docker": False,
                "auto_restart": True,
                "log_level": "INFO"
            },
            "openai": {
                "api_key": "",
                "default_model": "gpt-4o-mini",
                "default_temperature": 0.7
            }
        }
        
        # Wczytaj z pliku JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._config.update(file_config)
            except Exception as e:
                print(f"Błąd wczytywania konfiguracji projektu: {e}")
        
        # Wczytaj zmienne środowiskowe
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Nadpisz zmiennymi środowiskowymi
        if os.getenv("AI_PORT"):
            self._config["services"]["ai"]["port"] = int(os.getenv("AI_PORT"))
        if os.getenv("BACKEND_PORT"):
            self._config["services"]["backend"]["port"] = int(os.getenv("BACKEND_PORT"))
        if os.getenv("FRONTEND_PORT"):
            self._config["services"]["frontend"]["port"] = int(os.getenv("FRONTEND_PORT"))
        if os.getenv("AI_SERVICE_URL"):
            self._config["urls"]["ai_service"] = os.getenv("AI_SERVICE_URL")
        if os.getenv("BACKEND_SERVICE_URL"):
            self._config["urls"]["backend_service"] = os.getenv("BACKEND_SERVICE_URL")
        if os.getenv("OPENAI_API_KEY"):
            self._config["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("DEFAULT_MODEL"):
            self._config["openai"]["default_model"] = os.getenv("DEFAULT_MODEL")
        if os.getenv("DEFAULT_TEMPERATURE"):
            self._config["openai"]["default_temperature"] = float(os.getenv("DEFAULT_TEMPERATURE"))
        if os.getenv("ENVIRONMENT"):
            self._config["project"]["environment"] = os.getenv("ENVIRONMENT")
        if os.getenv("LOG_LEVEL"):
            self._config["deployment"]["log_level"] = os.getenv("LOG_LEVEL")
    
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
            print(f"Project config saved to {self.config_file}")
        except Exception as e:
            print(f"Błąd zapisywania konfiguracji projektu: {e}")
    
    def get_service_config(self, service_name):
        """Pobierz konfigurację konkretnego serwisu."""
        return self.get("services", service_name, default={})
    
    def get_service_port(self, service_name):
        """Pobierz port serwisu."""
        return self.get("services", service_name, "port", default=None)
    
    def get_service_url(self, service_name):
        """Pobierz URL serwisu."""
        if service_name == "frontend":
            return self.get("urls", "frontend_url")
        else:
            return self.get("urls", f"{service_name}_service")
    
    def get_all_ports(self):
        """Pobierz wszystkie porty serwisów."""
        return {
            "ai": self.get_service_port("ai"),
            "backend": self.get_service_port("backend"),
            "frontend": self.get_service_port("frontend")
        }
    
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
                            print(f"Project config file changed: {file_path}")
                            self.reload_config()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error watching project config files: {e}")
                time.sleep(5)
    
    def stop_watching(self):
        """Zatrzymaj obserwowanie plików."""
        self._watching = False

# Globalny instance
_project_config = None

def get_project_config():
    """Pobierz globalny config manager."""
    global _project_config
    if _project_config is None:
        _project_config = ProjectConfigManager()
    return _project_config

def get_ai_config():
    """Fallback dla AI config - przekieruj do lokalnego managera AI."""
    import sys
    import os
    
    # Próbuj zaimportować lokalny config manager AI
    try:
        ai_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai")
        sys.path.insert(0, ai_dir)
        from config.config_manager import get_ai_config as local_get_ai_config
        sys.path.remove(ai_dir)
        return local_get_ai_config()
    except ImportError:
        # Jeśli nie można zaimportować, zwróć project config jako fallback
        return get_project_config()

def get_backend_config():
    """Fallback dla Backend config - przekieruj do lokalnego managera Backend."""
    import sys
    import os
    
    # Próbuj zaimportować lokalny config manager Backend
    try:
        backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
        sys.path.insert(0, backend_dir)
        from config.config_manager import get_backend_config as local_get_backend_config
        sys.path.remove(backend_dir)
        return local_get_backend_config()
    except ImportError:
        # Jeśli nie można zaimportować, zwróć project config jako fallback
        return get_project_config()
