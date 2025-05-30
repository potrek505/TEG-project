import streamlit as st
import requests

# Load config from a file or define it here
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
    """Main Streamlit Your Finance Buddy Application"""
    
    def __init__(self):
        """Initialize the Your Finance Buddy application"""
        # Set page title and configuration
        st.set_page_config(
            page_title=config.get('app', {}).get('title', "Your Finance Buddy"),
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Add custom CSS for ChatGPT-like styling
        self._add_custom_css()
        
        # Get backend URL from environment or config
        self.backend_url = config.get('backend_url')
        
        # Check if backend is accessible
        try:
            response = requests.get(f"{self.backend_url}/api/health")
            if response.status_code != 200:
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
        except Exception as e:
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
        
        # Initialize session state for chat history and settings
        self._initialize_session_state()
    
    def _add_custom_css(self):
        """Add custom CSS for ChatGPT-like styling"""
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
        """Initialize session state variables"""
        # Set default model if not already in session state
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        # Initialize message history with default system message
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": config.get('default_system_message', "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.")}
            ]
    
    def display_welcome_message(self):
        """Display welcome message when chat is empty"""
        if len(st.session_state.messages) <= 1:  # Only system message
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
        """Display existing chat messages"""
        # Display all messages except the system message
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    def handle_user_input(self):
        """Process user input and generate response using backend API"""
        # Get user input from chat input box
        prompt = st.chat_input(config.get('chat_placeholder', "Ask Your Finance Buddy anything about money..."))
        
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown('<span class="thinking">Thinking...</span>', unsafe_allow_html=True)
                
                try:
                    # Call backend API
                    response = requests.post(
                        f"{self.backend_url}/api/agent-chat",
                        json={
                            "message": prompt,
                            "context": st.session_state.messages[0]["content"],
                            "model": st.session_state.openai_model,
                            "temperature": 0.7
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        assistant_response = response_data.get("response", "")
                        
                        # Update placeholder with the response
                        message_placeholder.markdown(assistant_response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        error_message = f"Error: API returned status {response.status_code}"
                        message_placeholder.error(error_message)
                        
                except Exception as e:
                    error_message = f"Error communicating with backend: {str(e)}"
                    message_placeholder.error(error_message)
    
    def clear_conversation(self):
        """Completely clear conversation and reset Your Finance Buddy memory"""
        try:
            # Call backend API to clear conversation memory
            response = requests.post(
                f"{self.backend_url}/api/clear-conversation",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                st.success("Conversation cleared successfully!")
            else:
                st.warning(f"Backend clear failed with status: {response.status_code}")
                
        except Exception as e:
            st.warning(f"Could not clear backend memory: {str(e)}")
        
        # Reset local session state completely
        st.session_state.messages = [
            {"role": "system", "content": config.get('default_system_message', "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.")}
        ]
        
        # Reset model to default
        st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        # Force a rerun to refresh the UI
        st.rerun()

    def run(self):
        """Run the Streamlit application"""
        # Title
        st.markdown('<div class="chat-title">Your Finance Buddy</div>', unsafe_allow_html=True)
        
        # Clear button in top right
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("🗑️ Clear", key="clear_chat"):
                self.clear_conversation()
        
        # Main chat container
        with st.container():
            # Show welcome message if no conversation yet
            self.display_welcome_message()
            
            # Display existing chat messages
            self.display_chat_messages()
        
        # Handle user input (this should be at the bottom)
        self.handle_user_input()

# Run the app
if __name__ == "__main__":
    app = ChatbotApp()
    app.run()