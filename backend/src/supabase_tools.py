from langchain_core.tools import tool

def create_query_supabase_tool(supabase_client):
    @tool
    def query_supabase(query_string: str) -> str:
        try:
            if not supabase_client:
                return "Supabase client is not configured. Please check your environment variables."
            
            parts = query_string.split(":")
            
            if len(parts) < 2:
                return "Invalid query format. Use 'table_name:column:value', 'table_name:limit:n', or 'table_name:all'."
            
            table_name = 'transactions'
            query_type = 'all'
            
            if query_type.lower() == "all":
                result = supabase_client.table(table_name).select("*").execute()
                return str(result.data)
            
            elif query_type.lower() == "limit":
                if len(parts) < 3:
                    return "Missing limit value. Use 'table_name:limit:n'."
                limit = int(parts[2].strip())
                result = supabase_client.table(table_name).select("*").limit(limit).execute()
                return str(result.data)
            
            else:
                if len(parts) < 3:
                    return "Missing value for column. Use 'table_name:column:value'."
                column = query_type
                value = parts[2].strip()
                
                allowed_columns = ["id", "transaction_id", "account_id", "booking_date", "value_date", 
                                   "booking_date_time", "transaction_amount", "transaction_currency", 
                                   "creditor_name", "creditor_account_iban", "debtor_name", 
                                   "debtor_account_iban", "remittance_information_unstructured", 
                                   "balance_after_transaction_amount", "balance_after_transaction_currency", 
                                   "balance_type", "internal_transaction_id"]

                if column not in allowed_columns:
                    return f"Column '{column}' does not exist in table '{table_name}'. Allowed columns are: {', '.join(allowed_columns)}"
                
                result = supabase_client.table(table_name).select("*").eq(column, value).execute()
                return str(result.data)
        
        except Exception as e:
            return f"Error querying Supabase: {e}"
    
    return query_supabase