import requests
import streamlit as st

class ApiClient:
    def __init__(self, backend_url):
        self.backend_url = backend_url
    
    def check_health(self):
        """Check backend API health"""
        try:
            response = requests.get(f"{self.backend_url}/health")
            if response.status_code != 200:
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
        except Exception as e:
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
    
    def get_conversation_history(self, session_id=None):
        """Get conversation history from backend"""
        try:
            params = {'session_id': session_id} if session_id else {}
            response = requests.get(f"{self.backend_url}/conversations", params=params)
            if response.status_code == 200:
                return response.json()['conversations']
            return []
        except Exception as e:
            st.error(f"Error fetching conversations: {e}")
            return []

    def get_sessions(self):
        """Get all sessions from backend"""
        try:
            response = requests.get(f"{self.backend_url}/sessions")
            if response.status_code == 200:
                return response.json()['sessions']
            return []
        except Exception as e:
            st.error(f"Error fetching sessions: {e}")
            return []

    def create_new_session(self):
        """Create a new session"""
        try:
            response = requests.post(f"{self.backend_url}/conversations/reset")
            if response.status_code == 200:
                return response.json()['session_id']
            return None
        except Exception as e:
            st.error(f"Error creating new session: {e}")
            return None

    def send_message(self, message, session_id=None):
        """Send message to AI backend"""
        try:
            data = {
                "message": message,
                "session_id": session_id
            }
            response = requests.post(f"{self.backend_url}/chat", json=data)
            return response.json()
        except Exception as e:
            st.error(f"Error sending message: {e}")
            return {"error": str(e)}

    def clear_conversation(self):
        """Clear conversation in backend"""
        try:
            response = requests.post(f"{self.backend_url}/api/clear-conversation")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error clearing conversation: {e}")
            return False
    
    def load_session_messages(self, session_id):
        """Load messages from a specific session"""
        if not session_id:
            return []
        
        conversations = self.get_conversation_history(session_id)
        messages = []
        
        for conv in conversations:
            messages.append({"role": "user", "content": conv['message']})
            messages.append({"role": "assistant", "content": conv['response']})
        
        return messages

    def reset_database(self):
        """Reset the entire database by calling the reset-database endpoint"""
        try:
            response = requests.post(f"{self.backend_url}/conversations/reset-database")
            if response.status_code == 200:
                return True
            else:
                st.error(f"Failed to reset database: {response.json().get('message', 'Unknown error')}")
                return False
        except Exception as e:
            st.error(f"Error resetting database: {str(e)}")
            return False