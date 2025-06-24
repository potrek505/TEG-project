from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from src.agents.basic_agent import BasicAgent
from src.agents.table_structures import ALL_TRANSACTIONS_TABLE_STRUCTURE
import os
import sys

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config.logging import get_logger

logger = get_logger(__name__)

class SQL_Agent(BasicAgent):
    """Klasa serwisu do interakcji z API OpenAI"""

    def __init__(self, db_uri=None):
        try:
            if db_uri is None:
                db_uri = os.getenv("transactions_db_uri")
            if not db_uri:
                logger.error("Database URI not provided")
                raise ValueError("Database URI is required")
                
            db = SQLDatabase.from_uri(db_uri)
            self.table_schema = ALL_TRANSACTIONS_TABLE_STRUCTURE
            super().__init__(tools=[QuerySQLDatabaseTool(db=db)])
            logger.info("SQL Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQL Agent: {str(e)}")
            raise

    def get_agent_response(self, human_message):
        """
        Uzyskaj odpowiedź używając agenta ReAct z narzędziami Supabase
        """
        try:
            if not human_message or not human_message.strip():
                logger.warning("Empty message provided to SQL Agent")
                return "Please provide a valid question."
                
            logger.info(f"Processing message with SQL Agent: {human_message[:50]}...")
            
            system_message = f"""
            You are a helpful assistant with access to a SQLite database. This database contains only one table: `all_transactions`.
            Always use only this table and its columns. Do not try to use or guess any other table or column names.

            {self.table_schema}

            Important conventions:
            - Negative amounts mean expenses, positive amounts mean income.
            - BLIK transactions can be found by the phrase 'BLIK' in the `remittance_info_unstructured` column.
            - Dates are in ISO format (e.g., '2025-04-30').
            - Full transaction data is available in the `raw_data` column as JSON.

            **If the user asks for recent transactions, always sort by the `booking_date` column in descending order.**
            **Never check for other tables or columns – always use only the above.**
            """
        
            prompt = PromptTemplate.from_template(
                system_message + "\n\n"
                "You are a helpful assistant. Use the tools below to assist you in answering the question.\n\n"
                "Available tools:\n{tool_names}\n\n"
                "Tools:\n{tools}\n\n"
                "When providing a response, follow this format:\n"
                "Action: <tool_name>\n"
                "Action Input: <input_for_tool>\n\n"
                "If no action is needed, respond with:\n"
                "Final Answer: <your_answer>\n\n"
                "Question:\n{input}\n\n"
                "Use the tools as needed to provide a helpful response:\n{agent_scratchpad}"
            )
        
            agent_executor = AgentExecutor.from_agent_and_tools(
                agent=create_react_agent(self.llm, self.tools, prompt),
                tools=self.tools,
                verbose=False,  # Changed from True to reduce noise
                handle_parsing_errors=True,
            )
        
            response = agent_executor.invoke({"input": human_message})
            result = response.get("output", "No response generated")
            logger.info("SQL Agent response generated successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error in SQL Agent: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again or rephrase your question."