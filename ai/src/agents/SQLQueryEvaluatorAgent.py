import sys
import os

# Dodaj ścieżkę do głównego katalogu projektu przed importami
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.basic_agent import BasicAgent
from src.agents.table_structures import ALL_TRANSACTIONS_TABLE_STRUCTURE
from config.logging import get_logger

logger = get_logger(__name__)

class SQLQueryEvaluatorAgent(BasicAgent):
    def __init__(self):
        try:
            super().__init__()
            self.table_schema = ALL_TRANSACTIONS_TABLE_STRUCTURE
            logger.info("SQLQueryEvaluatorAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQLQueryEvaluatorAgent: {str(e)}")
            raise

    def is_query_heavy(self, user_question):
        try:
            if not user_question or not user_question.strip():
                logger.warning("Empty question provided to SQLQueryEvaluatorAgent")
                return "NO"
                
            logger.info(f"Evaluating query complexity for: {user_question[:50]}...")
            
            system_message = (
                "You are an expert SQL database administrator. "
                "Given the following table schema and a user's question, answer YES if the question is likely to generate a heavy SQL query "
                "(e.g. a query that scans the whole table, lacks WHERE or LIMIT, or returns a large dataset), "
                "otherwise answer NO. Only answer YES or NO.\n\n"
                f"Table schema:\n{self.table_schema}\n\n"
                f"User question:\n{user_question}"
            )
            response = self.llm.invoke(system_message)
            result = response.content.strip().upper()
            
            # Ensure we only return YES or NO
            if result not in ["YES", "NO"]:
                logger.warning(f"Unexpected response from evaluator: {result}, defaulting to NO")
                result = "NO"
                
            logger.info(f"Query complexity evaluation result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in SQLQueryEvaluatorAgent: {str(e)}")
            return "NO"  # Default to light query on error