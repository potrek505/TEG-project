import os
import sys

# Użyj lokalnego systemu AI
ai_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ai_root not in sys.path:
    sys.path.insert(0, ai_root)

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config.logging import get_logger
from config.config_manager import get_ai_config

logger = get_logger(__name__)

class BasicAgent:
    def __init__(self, api_key=None, default_model=None, default_temperature=None, tools=None):
        try:
            # Get configuration
            config = get_ai_config()
            
            # Determine provider and settings
            provider = config.get("llm", "provider", default="openai")
            self.provider = provider
            
            if provider == "gemini":
                self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
                self.default_model = default_model or config.get("google_llm", "model", default="gemini-2.5-flash")
                self.default_temperature = float(default_temperature or config.get("google_llm", "temperature", default=0.7))
                
                if not self.api_key:
                    logger.error("Google API key not found")
                    raise ValueError("Google API key is required for Gemini")
                
                self.llm = ChatGoogleGenerativeAI(
                    google_api_key=self.api_key,
                    model=self.default_model,
                    temperature=self.default_temperature
                )
                logger.info(f"BasicAgent initialized with Gemini model: {self.default_model}")
                
            else:  # Default to OpenAI
                self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
                self.default_model = default_model or config.get("openai_llm", "model", default="gpt-4o-mini")
                self.default_temperature = float(default_temperature or config.get("openai_llm", "temperature", default=0.7))
                
                if not self.api_key:
                    logger.error("OpenAI API key not found")
                    raise ValueError("OpenAI API key is required")
                
                self.llm = ChatOpenAI(
                    api_key=self.api_key,
                    model=self.default_model,
                    temperature=self.default_temperature
                )
                logger.info(f"BasicAgent initialized with OpenAI model: {self.default_model}")
            
            self.tools = tools or []
            
        except Exception as e:
            logger.error(f"Failed to initialize BasicAgent: {str(e)}")
            raise

    def get_response(self, human_message, system_message="", **kwargs):
        raise NotImplementedError("Metoda get_response musi być zaimplementowana w klasie potomnej.")