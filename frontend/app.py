import streamlit as st
from src.settings import config
from src.session_state import initialize_session_state
from src.api_client import ApiClient
from src.ui_components import AppUI


def main():
    st.set_page_config(
        page_title=config["app"]["title"],
        layout="wide",
        initial_sidebar_state="expanded",
    )

    api_client = ApiClient(config["backend_url"])

    api_client.check_health()

    initialize_session_state(config)

    ui = AppUI(api_client, config)
    ui.run()


if __name__ == "__main__":
    main()