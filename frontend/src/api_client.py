import sys
import os
import requests
import streamlit as st

# Import shared logging system
from .logging_utils import get_logger

logger = get_logger(__name__)

class ApiClient:
    def __init__(self, backend_url):
        self.backend_url = backend_url
        if not backend_url:
            logger.error("Backend URL not provided")
            st.error("Backend configuration missing")
    
    def check_health(self):
        """Sprawdź stan zdrowia API backend"""
        try:
            logger.info("Checking backend health")
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code != 200:
                logger.warning(f"Backend API health check failed. Status: {response.status_code}")
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
            else:
                logger.info("Backend health check successful")
        except requests.exceptions.Timeout:
            logger.error("Backend health check timed out")
            st.error("Backend service is taking too long to respond")
        except Exception as e:
            logger.error(f"Cannot connect to backend: {str(e)}")
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
    
    def get_conversation_history(self, session_id=None):
        """Pobierz historię konwersacji z backendu"""
        try:
            logger.info(f"Fetching conversation history for session: {session_id[:8] if session_id else 'all'}")
            params = {'session_id': session_id} if session_id else {}
            response = requests.get(f"{self.backend_url}/conversations", params=params, timeout=30)
            if response.status_code == 200:
                return response.json()['conversations']
            else:
                logger.error(f"Failed to fetch conversations: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching conversations")
            st.error("Request timed out. Please try again.")
            return []
        except Exception as e:
            logger.error(f"Error fetching conversations: {str(e)}")
            st.error(f"Error fetching conversations: {e}")
            return []

    def get_sessions(self):
        """Pobierz wszystkie sesje z backendu"""
        try:
            logger.info("Fetching all sessions")
            response = requests.get(f"{self.backend_url}/sessions", timeout=30)
            if response.status_code == 200:
                return response.json()['sessions']
            else:
                logger.error(f"Failed to fetch sessions: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching sessions")
            st.error("Request timed out. Please try again.")
            return []
        except Exception as e:
            logger.error(f"Error fetching sessions: {str(e)}")
            st.error(f"Error fetching sessions: {e}")
            return []

    def create_new_session(self):
        """Utwórz nową sesję"""
        try:
            logger.info("Creating new session")
            response = requests.post(f"{self.backend_url}/conversations/reset", timeout=30)
            if response.status_code == 200:
                session_id = response.json()['session_id']
                logger.info(f"New session created: {session_id[:8]}")
                return session_id
            else:
                logger.error(f"Failed to create session: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            logger.error("Timeout creating session")
            st.error("Request timed out. Please try again.")
            return None
        except Exception as e:
            logger.error(f"Error creating new session: {str(e)}")
            st.error(f"Error creating new session: {e}")
            return None

    def send_message(self, message, session_id=None):
        """Wyślij wiadomość do backendu AI"""
        try:
            if not message or not message.strip():
                logger.warning("Attempted to send empty message")
                return {"error": "Message cannot be empty"}
                
            logger.info(f"Sending message for session: {session_id[:8] if session_id else 'unknown'}")
            data = {
                "message": message.strip(),
                "session_id": session_id
            }
            response = requests.post(f"{self.backend_url}/chat", json=data, timeout=120)
            result = response.json()
            
            if response.status_code == 200:
                logger.info("Message sent successfully")
            else:
                logger.error(f"Message sending failed: {response.status_code}")
                
            return result
        except requests.exceptions.Timeout:
            logger.error("Timeout sending message")
            return {"error": "Request timed out. Please try again."}
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {"error": f"Communication error: {str(e)}"}

    def clear_conversation(self):
        """Wyczyść konwersację w backendzie"""
        try:
            logger.info("Clearing conversation")
            response = requests.post(f"{self.backend_url}/api/clear-conversation", timeout=30)
            success = response.status_code == 200
            if success:
                logger.info("Conversation cleared successfully")
            else:
                logger.error(f"Failed to clear conversation: {response.status_code}")
            return success
        except requests.exceptions.Timeout:
            logger.error("Timeout clearing conversation")
            st.error("Request timed out. Please try again.")
            return False
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            st.error(f"Error clearing conversation: {e}")
            return False
    
    def load_session_messages(self, session_id):
        """Załaduj wiadomości z konkretnej sesji"""
        if not session_id:
            logger.warning("No session ID provided for loading messages")
            return []
        
        logger.info(f"Loading messages for session: {session_id[:8]}")
        conversations = self.get_conversation_history(session_id)
        messages = []
        
        for conv in conversations:
            if 'message' in conv and 'response' in conv:
                messages.append({"role": "user", "content": conv['message']})
                messages.append({"role": "assistant", "content": conv['response']})
        
        logger.info(f"Loaded {len(messages)} messages")
        return messages

    def reset_database(self):
        """Zresetuj całą bazę danych wywołując endpoint reset-database"""
        try:
            logger.warning("Resetting entire database")
            response = requests.post(f"{self.backend_url}/conversations/reset-database", timeout=30)
            if response.status_code == 200:
                logger.info("Database reset successful")
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"Failed to reset database: {error_msg}")
                st.error(f"Failed to reset database: {error_msg}")
                return False
        except requests.exceptions.Timeout:
            logger.error("Timeout resetting database")
            st.error("Request timed out. Please try again.")
            return False
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            st.error(f"Error resetting database: {str(e)}")
            return False

    def change_ai_provider(self, provider):
        """Zmień providera AI (OpenAI/Gemini)"""
        try:
            logger.info(f"Changing AI provider to: {provider}")
            response = requests.post(
                f"{self.backend_url}/config/ai-provider", 
                json={"provider": provider}, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Successfully changed AI provider to: {provider}")
                    return True, result.get("message", f"Provider changed to {provider}")
                else:
                    logger.error(f"Failed to change AI provider: {result.get('error')}")
                    return False, result.get("error", "Unknown error")
            else:
                logger.error(f"Failed to change AI provider. Status: {response.status_code}")
                return False, f"Server error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Timeout changing AI provider")
            return False, "Request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error changing AI provider: {str(e)}")
            return False, f"Error: {str(e)}"

    def get_ai_config(self):
        """Pobierz aktualną konfigurację AI przez backend"""
        try:
            logger.info("Fetching AI configuration")
            response = requests.get(f"{self.backend_url}/config/ai", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch AI config. Status: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching AI config: {str(e)}")
            return {}