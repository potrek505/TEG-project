import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.streamlit_config import ChatbotApp


if __name__ == "__main__":
    app = ChatbotApp()
    app.run()