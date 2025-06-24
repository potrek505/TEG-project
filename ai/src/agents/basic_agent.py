from langchain_openai import ChatOpenAI
import os
import sys

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config.logging import get_logger

logger = get_logger(__name__)

class BasicAgent:
    def __init__(self, api_key=None, default_model=None, default_temperature=None, tools=None):
        try:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            self.default_model = default_model or os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")
            self.default_temperature = float(default_temperature or os.environ.get("DEFAULT_TEMPERATURE", "0.7"))
            self.tools = tools or []
            
            if not self.api_key:
                logger.error("OpenAI API key not found")
                raise ValueError("OpenAI API key is required")
            
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.default_model,
                temperature=self.default_temperature
            )
            logger.info(f"BasicAgent initialized with model: {self.default_model}")
        except Exception as e:
            logger.error(f"Failed to initialize BasicAgent: {str(e)}")
            raise

    def get_response(self, human_message, system_message="", **kwargs):
        raise NotImplementedError("Metoda get_response musi być zaimplementowana w klasie potomnej.")