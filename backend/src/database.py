import sqlite3
import datetime

class ConversationDB:
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Inicjalizuje bazę danych"""
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
    
    def save_conversation(self, session_id, message, response):
        """Zapisuje konwersację do bazy danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO sessions (session_id, created_at) VALUES (?, ?)",
                (session_id, datetime.datetime.now().isoformat())
            )
        
        cursor.execute(
            "INSERT INTO conversations (session_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, message, response, datetime.datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id=None):
        """Pobiera historię konwersacji dla danej sesji lub wszystkie konwersacje"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute(
                "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
        else:
            cursor.execute("SELECT * FROM conversations ORDER BY timestamp")
        
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return conversations
    
    def get_all_sessions(self):
        """Pobiera wszystkie sesje"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sessions
    
    def clear_all_data(self):
        """Usuwa wszystkie dane z bazy danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations")
        cursor.execute("DELETE FROM sessions")
        
        conn.commit()
        conn.close()
        
        return True