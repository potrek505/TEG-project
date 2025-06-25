import os
import sys

# Użyj lokalnego systemu Backend
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

import sqlite3
import datetime
from config.logging import get_logger

logger = get_logger(__name__)

class ConversationDB:
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        try:
            self._initialize_db()
            logger.info(f"Database initialized successfully at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _initialize_db(self):
        """Inicjalizuje bazę danych"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    def save_conversation(self, session_id, message, response):
        """Zapisuje konwersację do bazy danych"""
        try:
            if not session_id or not message or not response:
                logger.error("Invalid data for conversation save")
                return False
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO sessions (session_id, created_at) VALUES (?, ?)",
                    (session_id, datetime.datetime.now().isoformat())
                )
                logger.info(f"New session created: {session_id[:8]}")
            
            cursor.execute(
                "INSERT INTO conversations (session_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, message, response, datetime.datetime.now().isoformat())
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Conversation saved for session {session_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            return False
    
    def get_conversation_history(self, session_id=None):
        """Pobiera historię konwersacji dla danej sesji lub wszystkie konwersacje"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute(
                    "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp",
                    (session_id,)
                )
                logger.info(f"Retrieved conversations for session {session_id[:8]}")
            else:
                cursor.execute("SELECT * FROM conversations ORDER BY timestamp")
                logger.info("Retrieved all conversations")
            
            conversations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return conversations
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    def get_all_sessions(self):
        """Pobiera wszystkie sesje"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return sessions
        except Exception as e:
            logger.error(f"Failed to get sessions: {str(e)}")
            return []
    
    def clear_all_data(self):
        """Usuwa wszystkie dane z bazy danych"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM sessions")
            
            conn.commit()
            conn.close()
            
            logger.warning("All database data has been cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            return False