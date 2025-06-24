import streamlit as st

class AppUI:
    def __init__(self, api_client, config):
        self.api_client = api_client
        self.config = config
    
    def setup_sidebar(self):
        """Skonfiguruj pasek boczny z zarządzaniem sesjami"""
        st.sidebar.title("💬 Sesje Konwersacji")

        if st.sidebar.button("🆕 Nowa Konwersacja", use_container_width=True):
            if self.api_client.clear_conversation():
                new_session_id = self.api_client.create_new_session()
                if new_session_id:
                    st.session_state.current_session_id = new_session_id
                    st.session_state.messages = []
                    st.session_state.viewing_mode = False
                    st.session_state.viewing_session_id = None
                    st.success("🆕 Nowa konwersacja rozpoczęta!")
                    st.rerun()
        
        if st.sidebar.button("🗑️ Clear All Conversation Data", use_container_width=True):
            if self.api_client.reset_database():
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.session_state.viewing_mode = False
                st.session_state.viewing_session_id = None
                st.success("✅ All conversation data has been deleted")
                st.rerun()
            else:
                st.error("❌ Failed to clear database")

        if st.session_state.current_session_id:
            if st.sidebar.button("🔄 Back to Current Chat", use_container_width=True, type="primary"):
                st.session_state.messages = self.api_client.load_session_messages(
                    st.session_state.current_session_id
                )
                st.session_state.viewing_mode = False
                st.session_state.viewing_session_id = None
                st.success("🔄 Returned to active chat!")
                st.rerun()
        else:
            st.sidebar.info("Start a new conversation to begin chatting.")

        st.sidebar.markdown("---")

        sessions = self.api_client.get_sessions()
        
        if sessions:
            st.sidebar.subheader("📝 Previous Sessions")
            for session in sessions:
                session_id = session['session_id']
                session_preview = f"{session_id[:8]}..."
                created_at = session['created_at']
                
                if session_id == st.session_state.current_session_id and not st.session_state.viewing_mode:
                    icon = "🟢"
                    button_text = f"{icon} {session_preview} (ACTIVE)\n{created_at}"
                elif session_id == st.session_state.current_session_id and st.session_state.viewing_mode:
                    icon = "🔵"
                    button_text = f"{icon} {session_preview} (YOUR ACTIVE)\n{created_at}"
                else:
                    icon = "👁️"
                    button_text = f"{icon} {session_preview}\n{created_at}"
                
                if st.sidebar.button(
                    button_text, 
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    if session_id == st.session_state.current_session_id:
                        st.session_state.messages = self.api_client.load_session_messages(session_id)
                        st.session_state.viewing_mode = False
                        st.session_state.viewing_session_id = None
                    else:
                        st.session_state.viewing_mode = True
                        st.session_state.viewing_session_id = session_id
                        st.session_state.messages = self.api_client.load_session_messages(session_id)
                    st.rerun()
        else:
            st.sidebar.write("No previous sessions found")

        if st.session_state.viewing_mode:
            st.sidebar.markdown("---")
            if st.session_state.viewing_session_id == st.session_state.current_session_id:
                st.sidebar.write(f"🔵 **Viewing Your Active Session:** {st.session_state.viewing_session_id[:8]}...")
                st.sidebar.info("💡 This is your current session in view mode. Click 'Back to Current Chat' to continue.")
            else:
                st.sidebar.write(f"👁️ **Viewing Session:** {st.session_state.viewing_session_id[:8]}...")
                st.sidebar.info("💡 This is view-only mode. Use 'Back to Current Chat' or create a new session.")
        elif st.session_state.current_session_id:
            st.sidebar.markdown("---")
            st.sidebar.write(f"🟢 **Active Session:** {st.session_state.current_session_id[:8]}...")

    def display_welcome_message(self):
        """Wyświetl wiadomość powitalną na podstawie stanu aplikacji"""
        if len(st.session_state.messages) == 0 and not st.session_state.viewing_mode:
            st.markdown("""
            **Welcome to Your Finance Buddy! 💰**
            
            I'm your AI assistant ready to help with:
            - Investment advice and portfolio management
            - Budgeting and expense tracking
            - Financial planning and goal setting
            - Tax strategies and retirement planning
            
            Start a new conversation or select a previous session from the sidebar!
            """)
        elif len(st.session_state.messages) == 0 and st.session_state.viewing_mode:
            st.info("📖 You are viewing a previous conversation. This session appears to be empty.")
    
    def display_chat_messages(self):
        """Wyświetl historię wiadomości czatu"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def handle_user_input(self):
        """Obsłuż wprowadzanie danych przez użytkownika w czacie"""
        if st.session_state.viewing_mode:
            if st.session_state.viewing_session_id == st.session_state.current_session_id:
                st.info("👁️ **View mode:** You're viewing your active session. Click on it in the sidebar to continue chatting.")
            else:
                st.info("👁️ **View-only mode:** You're viewing a previous conversation. Click on your active session in the sidebar or start typing below to create a new session.")
            return
        
        prompt = st.chat_input(self.config.get('chat_placeholder', "Ask Your Finance Buddy anything about money..."))
        
        if prompt:
            if not st.session_state.current_session_id:
                self.api_client.clear_conversation()
                
                new_session_id = self.api_client.create_new_session()
                if new_session_id:
                    st.session_state.current_session_id = new_session_id
                else:
                    st.error("Failed to create new session")
                    return

            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    response = self.api_client.send_message(
                        prompt,
                        st.session_state.current_session_id
                    )
                    
                    if "error" not in response:
                        assistant_response = response.get("response", "")
                        message_placeholder.markdown(assistant_response)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        error_message = f"Error: {response['error']}"
                        message_placeholder.error(error_message)
                        
                except Exception as e:
                    error_message = f"Error communicating with backend: {str(e)}"
                    message_placeholder.error(error_message)

    def run(self):
        """Uruchom interfejs użytkownika aplikacji"""
        self.setup_sidebar()
        
        if st.session_state.viewing_mode:
            st.title("👁️ Your Finance Buddy - Viewing Previous Session")
        else:
            st.title("💰 Your Finance Buddy")
        
        with st.container():
            self.display_welcome_message()
            self.display_chat_messages()
        
        self.handle_user_input()