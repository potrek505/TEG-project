import os
import sys

# Użyj lokalnego systemu AI
ai_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ai_root not in sys.path:
    sys.path.insert(0, ai_root)

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from src.agents.SQL_Agent import SQL_Agent
from src.agents.SQLQueryEvaluatorAgent import SQLQueryEvaluatorAgent
from src.rags.advanced_rag_config import AdaptiveRAG
import sqlite3
from config.logging import get_logger
from config.config_manager import get_ai_config

logger = get_logger(__name__)


class State(TypedDict):
    graph_state: str
    rag: AdaptiveRAG | None
    sql_agent: SQL_Agent | None
    evaluate_sql_statement_agent: SQLQueryEvaluatorAgent | None
    user_message: str | None
    agent_response: str | None
    rag_response: str | None
    is_sql_query_heavy: str | None

def node_1(state):
    logger.info("Executing Node 1 - checking RAG existence")
    if state.get("rag") is not None:
        logger.info("RAG exists, proceeding to rag_node")
    else:
        logger.info("RAG does not exist, proceeding to evaluate_sql_statement")
    return state

def evaluate_sql_statement(state):
    logger.info("Evaluating SQL query complexity")
    try:
        if state.get("evaluate_sql_statement_agent") is None:
            state["evaluate_sql_statement_agent"] = SQLQueryEvaluatorAgent()
        user_message = state.get("user_message")
        response = state["evaluate_sql_statement_agent"].is_query_heavy(user_message)
        if response == "YES":
            logger.info("Query is heavy - will create RAG")
            state["is_sql_query_heavy"] = "YES"
        else:
            logger.info("Query is light - will use agent")
            state["is_sql_query_heavy"] = "NO"
        return state
    except Exception as e:
        logger.error(f"Error evaluating SQL statement: {str(e)}")
        state["is_sql_query_heavy"] = "NO"  # Fallback to agent
        return state

def rag_node(state):
    logger.info("Processing with RAG")
    try:
        user_message = state.get("user_message")
        rag_response = state["rag"].query(user_message)
        logger.info("RAG response generated successfully")
        return {
            "user_message": user_message,
            "rag_response": rag_response["answer"]
        }
    except Exception as e:
        logger.error(f"Error in RAG node: {str(e)}")
        return {
            "user_message": state.get("user_message"),
            "rag_response": "Sorry, I encountered an error processing your request with the knowledge base."
        }

def agent_node(state):
    logger.info("Processing with SQL Agent")
    try:
        if state.get("sql_agent") is None:
            state["sql_agent"] = SQL_Agent()
        user_message = state.get("user_message")
        agent_response = state["sql_agent"].get_agent_response(user_message)
        logger.info("Agent response generated successfully")
        return {
            "user_message": user_message,
            "agent_response": agent_response,
        }
    except Exception as e:
        logger.error(f"Error in agent node: {str(e)}")
        return {
            "user_message": state.get("user_message"),
            "agent_response": "Sorry, I encountered an error processing your request with the database.",
        }

def create_rag(state):
    logger.info("Creating new RAG instance")
    try:
        # Pobierz ścieżkę do bazy danych ze zmiennych środowiskowych lub konfiguracji
        db_path = os.environ.get("transactions_db_path")
        if not db_path:
            config = get_ai_config()
            db_path = config.get("database", "path")
            
        if not db_path or not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return state
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM all_transactions LIMIT 1000")  # Limit for performance
        rows = cursor.fetchall()
        conn.close()
        
        logger.info(f"Retrieved {len(rows)} transactions for RAG creation")
        
        if rows:
            all_text = "\n".join([str(item) for item in rows])
            docs = [Document(page_content=all_text)]
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
            llm = state["evaluate_sql_statement_agent"].llm
            state["rag"] = AdaptiveRAG(llm, retriever, vectorstore)
            logger.info("RAG created successfully")
        else:
            logger.warning("No transactions found for RAG creation")
        return state
    except Exception as e:
        logger.error(f"Error creating RAG: {str(e)}")
        return state

builder = StateGraph(State)
builder.add_node("Node1", node_1)
builder.add_node("rag_response_node", rag_node)
builder.add_node("agent_response_node", agent_node)
builder.add_node("evaluate_sql_statement", evaluate_sql_statement)
builder.add_node("create_rag", create_rag)

builder.add_edge(START, "Node1")
builder.add_conditional_edges("Node1", lambda state: "rag_response_node" if state.get("rag") is not None else "evaluate_sql_statement")
builder.add_conditional_edges("evaluate_sql_statement", lambda state: "create_rag" if state.get("is_sql_query_heavy") == "YES" else "agent_response_node")
builder.add_edge("create_rag", "rag_response_node")
builder.add_edge("rag_response_node", END)
builder.add_edge("agent_response_node", END)


def get_dynamic_rag_graph():
    return builder.compile()