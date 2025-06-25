"""
Prosty menedżer konfiguracji dla serwisu AI.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class AIConfigManager:
    """Prosty menedżer konfiguracji dla AI."""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "ai_config.json"
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
            "llm": {
                "provider": "openai",
                "model": "gpt-4o-mini", 
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "google_llm": {
                "model": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "openai_llm": {
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "rag": {
                "enabled": True,
                "chunk_size": 1000,
                "max_docs": 10
            },
            "server": {
                "port": 5001,
                "debug": False
            }
        }
        
        # Wczytaj z pliku JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._config.update(file_config)
            except Exception as e:
                print(f"Błąd wczytywania konfiguracji AI: {e}")
        
        # Wczytaj zmienne środowiskowe
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Nadpisz zmiennymi środowiskowymi
        if os.getenv("LLM_PROVIDER"):
            self._config["llm"]["provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_MODEL"):
            self._config["llm"]["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_TEMPERATURE"):
            self._config["llm"]["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
        if os.getenv("RAG_ENABLED"):
            self._config["rag"]["enabled"] = os.getenv("RAG_ENABLED").lower() == "true"
        if os.getenv("AI_PORT"):
            self._config["server"]["port"] = int(os.getenv("AI_PORT"))
        if os.getenv("AI_DEBUG"):
            self._config["server"]["debug"] = os.getenv("AI_DEBUG").lower() == "true"
        if os.getenv("GOOGLE_API_KEY"):
            if "google_llm" not in self._config:
                self._config["google_llm"] = {}
            self._config["google_llm"]["api_key"] = os.getenv("GOOGLE_API_KEY")
        if os.getenv("DATABASE_PATH"):
            self._config["database"]["path"] = os.getenv("transactions_db_path")
    
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
            print(f"AI config saved to {self.config_file}")
        except Exception as e:
            print(f"Błąd zapisywania konfiguracji AI: {e}")
    
    def get_server_config(self):
        """Pobierz konfigurację serwera."""
        return self.get("server", default={})
    
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
                            print(f"AI config file changed: {file_path}")
                            self.reload_config()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error watching AI config files: {e}")
                time.sleep(5)
    
    def stop_watching(self):
        """Zatrzymaj obserwowanie plików."""
        self._watching = False

# Globalny instance
_ai_config = None

def get_ai_config():
    """Pobierz globalny config manager."""
    global _ai_config
    if _ai_config is None:
        _ai_config = AIConfigManager()
    return _ai_config
