import streamlit as st

def initialize_session_state(config):
    """Inicjalizuj zmienne stanu sesji Streamlit"""
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "viewing_mode" not in st.session_state:
        st.session_state.viewing_mode = False
    
    if "viewing_session_id" not in st.session_state:
        st.session_state.viewing_session_id = None