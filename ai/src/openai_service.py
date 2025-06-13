from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from supabase import create_client
from src.tools.supabase_tools import create_query_supabase_tool

class OpenAIService:
    """Service class for interacting with OpenAI API"""
    
    def __init__(self, api_key, default_model, default_temperature,
                 supabase_url, supabase_key):
        self.api_key = api_key
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = create_client(supabase_url, supabase_key)
        self.memory = ConversationBufferMemory(return_messages=True)

    
    def clear_conversation(self):
        self.memory.clear()
    
    def get_agent_response(self, human_message, system_message="", model=None, temperature=None):
        """
        Get a response using a ReAct agent with Supabase tools
        
        Args:
            human_message (str): The user message to send to the agent
            system_message (str, optional): System message to set context
            model (str, optional): Model to use, defaults to the instance default
            temperature (float, optional): Temperature setting, defaults to the instance default
            
        Returns:
            str: The response from the agent or None if an error occurred
        """
        try:
            model = model or self.default_model
            temperature = temperature or self.default_temperature
            
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model,
                temperature=temperature
            )
            
            messages = []
            system_message = """
                You are a helpful assistant with access to a database. The database contains the following table:

                Table: transactions
                Columns:
                - id (serial, not null): Unique identifier for each transaction
                - transaction_id (character varying(50), not null): Unique ID for the transaction
                - account_id (integer, not null): ID of the associated account
                - booking_date (date, not null): Date when the transaction was booked
                - value_date (date, not null): Date when the transaction value was applied
                - booking_date_time (timestamp, not null): Exact time of booking
                - transaction_amount (numeric(15, 2), not null): Amount of the transaction
                - transaction_currency (character varying(10), not null): Currency of the transaction
                - creditor_name (character varying(255), null): Name of the creditor
                - creditor_account_iban (character varying(34), null): IBAN of the creditor's account
                - debtor_name (character varying(255), null): Name of the debtor
                - debtor_account_iban (character varying(34), null): IBAN of the debtor's account
                - remittance_information_unstructured (text, null): Additional information about the transaction
                - balance_after_transaction_amount (numeric(15, 2), null): Account balance after the transaction
                - balance_after_transaction_currency (character varying(10), null): Currency of the balance
                - balance_type (character varying(50), null): Type of balance (e.g., available, booked)
                - internal_transaction_id (character varying(100), not null): Internal ID for the transaction

                You can use the `query_supabase` tool to query this table. Always include the `transaction_id` in your responses to help the user refer to specific transactions in follow-up questions.

                ### How to use the `query_supabase` tool:
                1. Fetch all records: `transactions:all`
                2. Fetch a limited number of records: `transactions:limit:<n>`
                3. Fetch records by a specific column value: `transactions:<column>:<value>`

                Use this information to answer questions or query the database effectively.
                """
            if system_message:
                messages.append(SystemMessage(content=system_message))
        
            messages.append(HumanMessage(content=human_message))
    
            query_supabase_tool = create_query_supabase_tool(self.supabase_client)
            tools = [query_supabase_tool]
        
            prompt = PromptTemplate.from_template(
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
                agent=create_react_agent(llm, tools, prompt),
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
                memory=self.memory 
            )
        
            response = agent_executor.invoke({"input": human_message})
        
            return response.get("output", "No response generated")
        
        except Exception as e:
            print(f"[ERROR] Error in agent: {e}")
            return None