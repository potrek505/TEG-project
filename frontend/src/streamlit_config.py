import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'app': {
        'title': "Your Finance Buddy",
        'layout': "wide"
    },
    'backend_url': f"http://localhost:{os.environ.get('BACKEND_PORT')}",
    'default_model': "gpt-4o-mini",
    'default_system_message': "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.",
    'chat_placeholder': "Ask Your Finance Buddy anything about money...",
    'app_title': "Your Finance Buddy"
}

class ChatbotApp:
    
    def __init__(self):
        """Initialize the Your Finance Buddy application"""
        st.set_page_config(
            page_title=config.get('app', {}).get('title', "Your Finance Buddy"),
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        self.backend_url = config.get('backend_url')
        
        try:
            response = requests.get(f"{self.backend_url}/health")
            if response.status_code != 200:
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
        except Exception as e:
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
        
        self._initialize_session_state()
        
    def _initialize_session_state(self):

        if "openai_model" not in st.session_state:
            st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": config.get('default_system_message', "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.")}
            ]
    
    def display_welcome_message(self):
        if len(st.session_state.messages) <= 1:
            st.markdown("""
            **How can I help you today?**
            
            I'm your AI assistant, ready to answer questions and help with various tasks.
            Just type your message below to get started!
            """)
    
    def display_chat_messages(self):
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    def handle_user_input(self):
        prompt = st.chat_input(config.get('chat_placeholder', "Ask Your Finance Buddy anything about money..."))
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    response = requests.post(
                        f"{self.backend_url}/chat",
                        json={
                            "message": prompt,
                            "user_id": "streamlit_user"
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        assistant_response = response_data.get("response", "")
                        
                        message_placeholder.markdown(assistant_response)
                        
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        error_message = f"Error: API returned status {response.status_code}"
                        message_placeholder.error(error_message)
                        
                except Exception as e:
                    error_message = f"Error communicating with backend: {str(e)}"
                    message_placeholder.error(error_message)
    
    def clear_conversation(self):
        st.session_state.messages = [
            {"role": "system", "content": config.get('default_system_message', "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.")}
        ]
        
        st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        st.success("Conversation cleared!")
        st.rerun()

    def run(self):
        st.title("Your Finance Buddy")
        
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("🗑️ Clear", key="clear_chat"):
                self.clear_conversation()
        
        with st.container():
            self.display_welcome_message()
            
            self.display_chat_messages()
        
        self.handle_user_input()