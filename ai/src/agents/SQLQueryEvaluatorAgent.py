from src.agents.basic_agent import BasicAgent
from src.agents.table_structures import ALL_TRANSACTIONS_TABLE_STRUCTURE

class SQLQueryEvaluatorAgent(BasicAgent):
    def __init__(self):
        super().__init__()
        self.table_schema = ALL_TRANSACTIONS_TABLE_STRUCTURE

    def is_query_heavy(self, user_question):
        system_message = (
            "You are an expert SQL database administrator. "
            "Given the following table schema and a user's question, answer YES if the question is likely to generate a heavy SQL query "
            "(e.g. a query that scans the whole table, lacks WHERE or LIMIT, or returns a large dataset), "
            "otherwise answer NO. Only answer YES or NO.\n\n"
            f"Table schema:\n{self.table_schema}\n\n"
            f"User question:\n{user_question}"
        )
        response = self.llm.invoke(system_message)
        return response.content