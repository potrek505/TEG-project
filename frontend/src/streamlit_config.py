import streamlit as st
import requests

config = {
    'app': {
        'title': "Your Finance Buddy",
        'layout': "wide"
    },
    'backend_url': "http://localhost:55000",
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
        
        self._add_custom_css()
        
        self.backend_url = config.get('backend_url')
        
        try:
            response = requests.get(f"{self.backend_url}/api/health")
            if response.status_code != 200:
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
        except Exception as e:
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
        
        self._initialize_session_state()
    
    def _add_custom_css(self):
        st.markdown("""
        <style>
        /* Hide Streamlit branding and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container styling */
        .stApp {
            background-color: #212121;
        }
        
        /* Chat container */
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Title styling */
        .chat-title {
            text-align: center;
            color: white;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 2rem;
            padding: 1rem;
        }
        
        /* Message styling */
        .stChatMessage {
            background-color: transparent !important;
            padding: 1rem 0 !important;
        }
        
        /* User message styling */
        .stChatMessage[data-testid="chat-message-user"] {
            background-color: transparent !important;
        }
        
        .stChatMessage[data-testid="chat-message-user"] > div {
            background-color: #2f2f2f !important;
            border-radius: 18px !important;
            padding: 12px 16px !important;
            margin-left: 20% !important;
            color: white !important;
        }
        
        /* Assistant message styling */
        .stChatMessage[data-testid="chat-message-assistant"] {
            background-color: transparent !important;
        }
        
        .stChatMessage[data-testid="chat-message-assistant"] > div {
            background-color: #444654 !important;
            border-radius: 18px !important;
            padding: 12px 16px !important;
            margin-right: 20% !important;
            color: white !important;
        }
        
        /* Chat input styling */
        .stChatInputContainer {
            background-color: #40414f !important;
            border-radius: 12px !important;
            border: 1px solid #565869 !important;
            margin: 1rem auto !important;
            max-width: 800px !important;
        }
        
        .stChatInputContainer input {
            background-color: transparent !important;
            color: white !important;
            border: none !important;
            font-size: 16px !important;
        }
        
        .stChatInputContainer input::placeholder {
            color: #8e8ea0 !important;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #10a37f !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            font-weight: 500 !important;
            transition: background-color 0.2s !important;
        }
        
        .stButton > button:hover {
            background-color: #1a7f64 !important;
        }
        
        /* Clear button styling */
        .clear-button {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999;
        }
        
        /* Avatar styling */
        .stChatMessage img {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
        }
        
        /* Welcome message styling */
        .welcome-container {
            text-align: center;
            color: #8e8ea0;
            padding: 2rem;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .welcome-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1rem;
        }
        
        .welcome-subtitle {
            font-size: 1rem;
            line-height: 1.5;
        }
        
        /* Thinking indicator */
        .thinking {
            color: #8e8ea0 !important;
            font-style: italic !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
            <div class="welcome-container">
                <div class="welcome-title">How can I help you today?</div>
                <div class="welcome-subtitle">
                    I'm your AI assistant, ready to answer questions and help with various tasks.
                    Just type your message below to get started!
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def display_chat_messages(self):
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    def handle_user_input(self):
        if prompt := st.chat_input(config.get('chat_placeholder', "Ask Your Finance Buddy anything about money...")):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/agent-chat",
                        json={
                            "message": prompt,
                            "context": st.session_state.messages[0]["content"],
                            "model": st.session_state.openai_model,
                            "temperature": 0.7
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        assistant_response = response_data.get("response", "No response received")
                        
                        st.markdown(assistant_response)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        error_message = f"Error: API returned status {response.status_code}"
                        st.error(error_message)
                        
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Please check if the server is running.")
                except Exception as e:
                    st.error(f"Error communicating with backend: {str(e)}")
    
    def clear_conversation(self):
        try:
            response = requests.post(
                f"{self.backend_url}/api/clear-conversation",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                st.success("Conversation cleared successfully!")
            else:
                st.warning(f"Backend clear failed with status: {response.status_code}")
                
        except Exception as e:
            st.warning(f"Could not clear backend memory: {str(e)}")
        
        st.session_state.messages = [
            {"role": "system", "content": config.get('default_system_message', "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.")}
        ]
        
        st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        st.rerun()

    def run(self):
        st.markdown('<div class="chat-title">Your Finance Buddy</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("🗑️ Clear", key="clear_chat"):
                self.clear_conversation()
        
        with st.container():
            self.display_welcome_message()
            self.display_chat_messages()
            self.handle_user_input()

if __name__ == "__main__":
    app = ChatbotApp()
    app.run()