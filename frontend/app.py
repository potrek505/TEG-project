import sys
import os
import streamlit as st

from src.settings import config, get_config, config_manager
from src.session_state import initialize_session_state
from src.api_client import ApiClient
from src.ui_components import AppUI
from src.logging_utils import init_logging, get_logger

# Inicjalizacja systemu logowania
init_logging()
logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting frontend application")
        
        # Get Streamlit configuration from config manager
        app_config = config_manager.get("app", default={})
        
        st.set_page_config(
            page_title=app_config.get("title", "Your Finance Buddy"),
            layout=app_config.get("layout", "wide"),
            initial_sidebar_state="expanded"
        )

        current_config = get_config()
        
        if not current_config.get("backend_url"):
            st.error("Backend URL not configured. Please check environment variables.")
            logger.error("Backend URL not configured")
            return

        api_client = ApiClient(current_config["backend_url"])
        api_client.check_health()

        initialize_session_state(current_config)

        ui = AppUI(api_client, current_config)
        ui.run()
        
        logger.info("Frontend application running successfully")
        
    except Exception as e:
        logger.error(f"Error in frontend main: {str(e)}")
        st.error("An error occurred while starting the application. Please refresh the page.")

if __name__ == "__main__":
    main()