import streamlit as st
import sys
import os
from src.settings import config
from src.session_state import initialize_session_state
from src.api_client import ApiClient
from src.ui_components import AppUI

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_logging import setup_logging

# Konfiguracja loggera używając shared_logging
logger = setup_logging("frontend")

def main():
    try:
        logger.info("Starting frontend application")
        
        st.set_page_config(
            page_title=config["app"]["title"],
            layout="wide",
            initial_sidebar_state="expanded",
        )

        if not config.get("backend_url"):
            st.error("Backend URL not configured. Please check environment variables.")
            logger.error("Backend URL not configured")
            return

        api_client = ApiClient(config["backend_url"])
        api_client.check_health()

        initialize_session_state(config)

        ui = AppUI(api_client, config)
        ui.run()
        
        logger.info("Frontend application running successfully")
        
    except Exception as e:
        logger.error(f"Error in frontend main: {str(e)}")
        st.error("An error occurred while starting the application. Please refresh the page.")

if __name__ == "__main__":
    main()