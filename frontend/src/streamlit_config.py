import streamlit as st
import requests

# Load config from a file or define it here
config = {
    'app': {
        'title': "AI Chatbot",
        'layout': "wide"
    },
    'backend_url': "http://localhost:55000",  # Backend API URL
    'default_model': "gpt-4o-mini",
    'default_system_message': "You are a helpful, polite academic teacher answering students' questions",
    'chat_placeholder': "Hi, how can I help you?",
    'app_title': "ChatBot"
}

class ChatbotApp:
    """Main Streamlit Chatbot Application"""
    
    def __init__(self):
        """Initialize the chatbot application"""
        # Load environment variables
        
        # Set page title and configuration
        st.set_page_config(
            page_title=config.get('app', {}).get('title', "AI Chatbot"),
            layout=config.get('app', {}).get('layout', "wide")
        )
        
        # Get backend URL from environment or config
        self.backend_url = config.get('backend_url')
        
        # Check if backend is accessible
        try:
            response = requests.get(f"{self.backend_url}/api/health")
            if response.status_code != 200:
                st.warning(f"Backend API is not responding properly. Status: {response.status_code}")
                # Continue instead of stopping
        except Exception as e:
            st.warning(f"Cannot connect to backend at {self.backend_url}: {str(e)}")
            # Continue instead of stopping
        
        # Initialize session state for chat history and settings
        self._initialize_session_state()
        
    def _initialize_session_state(self):
        """Initialize session state variables"""
        # Set default model if not already in session state
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = config.get('default_model', "gpt-4o-mini")
        
        # Initialize message history with default system message
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": config.get('default_system_message', "You are a helpful, polite academic teacher answering students' questions")}
            ]
    
    
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
        prompt = st.chat_input(config.get('chat_placeholder', "Hi, how can I help you?"))
        
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    # Call backend API
                    response = requests.post(
                        f"{self.backend_url}/api/chat",
                        json={
                            "message": prompt,
                            "context": st.session_state.messages[0]["content"],
                            "model": st.session_state.openai_model,
                            "temperature": 0.7  # Could be configurable in the UI
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
    
    def run(self):
        """Run the Streamlit application"""
        st.title("ChatBot")
        
        # Dodaj prosty element UI, aby sprawdzić czy cokolwiek się renderuje
        st.write("Welcome to the chatbot interface!")
        
        # Display existing chat messages
        self.display_chat_messages()
        
        # Handle user input
        self.handle_user_input()
        
        # Add reset button at the bottom
        if st.button("Clear chat"):
            # Keep only the system message
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()