from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from src.agents.basic_agent import BasicAgent
from dotenv import load_dotenv
import os


load_dotenv()
class SQL_Agent(BasicAgent):
    """Service class for interacting with OpenAI API"""

    def __init__(self, db_uri = os.environ.get("transations_db_uri")):
        db = SQLDatabase.from_uri(db_uri)
        super().__init__(tools=[QuerySQLDatabaseTool(db=db)])

    def get_agent_response(self, human_message):
        """
        Get a response using a ReAct agent with Supabase tools
        """
        try:
            system_message = """
            You are a helpful assistant with access to a SQLite database. This database contains only one table: `all_transactions`.
            Always use only this table and its columns. Do not try to use or guess any other table or column names.

            Table structure for `all_transactions`:
            1. id - INTEGER (primary key)
            2. account_id - TEXT - account identifier
            3. transaction_id - TEXT - unique transaction ID
            4. internal_transaction_id - TEXT - internal transaction ID
            5. booking_date - TEXT - booking date (format: YYYY-MM-DD)
            6. value_date - TEXT - value date (format: YYYY-MM-DD)
            7. booking_date_time - TEXT - full date and time (ISO 8601)
            8. amount - REAL - transaction amount (negative = expense, positive = income)
            9. currency - TEXT - currency (e.g., 'PLN')
            10. remittance_info_unstructured - TEXT - transaction description
            11. remittance_info_array - TEXT - description as JSON array
            12. creditor_name - TEXT - creditor name
            13. creditor_iban - TEXT - creditor IBAN
            14. debtor_name - TEXT - debtor name
            15. debtor_iban - TEXT - debtor IBAN
            16. balance_after_amount - REAL - balance after transaction
            17. balance_after_currency - TEXT - balance currency
            18. balance_after_type - TEXT - balance type (e.g., 'interimBooked')
            19. raw_data - TEXT - full transaction data as JSON

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
                "Chat history:\n{history}\n\n"
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
                verbose=True,
                handle_parsing_errors=True,
                memory=self.memory 
            )
        
            response = agent_executor.invoke({"input": human_message})
        
            return response.get("output", "No response generated")
        
        except Exception as e:
            print(f"[ERROR] Error in agent: {e}")
            return None