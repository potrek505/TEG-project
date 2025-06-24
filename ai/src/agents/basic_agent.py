from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

load_dotenv()

class BasicAgent:
    def __init__(self, api_key = os.environ.get("OPENAI_API_KEY"), default_model = os.environ.get("DEFAULT_MODEL"), default_temperature= os.environ.get("DEFAULT_TEMPERATURE"), tools=None):
        self.api_key = api_key
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.tools = tools or []
        

        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.default_model,
            temperature=self.default_temperature
        )


    def get_response(self, human_message, system_message="", **kwargs):
        raise NotImplementedError("Metoda get_response musi być zaimplementowana w klasie potomnej.")