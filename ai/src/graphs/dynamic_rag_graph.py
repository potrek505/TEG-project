from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from src.agents.SQL_Agent import SQL_Agent
from src.agents.SQLQueryEvaluatorAgent import SQLQueryEvaluatorAgent
from src.rags.advanced_rag_config import AdaptiveRAG
import sqlite3
from dotenv import load_dotenv
import os
load_dotenv()


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
    print("--- Node 1 ---")
    if state.get("rag") is not None:
        print("RAG istnieje! Przechodzę do rag_node.")
    else:
        print("RAG nie istnieje! Przechodzę do evaluate_sql_statement.")
    return state

def evaluate_sql_statement(state):
    print("Ewaluacja zapytania SQL!")
    if state.get("evaluate_sql_statement_agent") is None:
        state["evaluate_sql_statement_agent"] = SQLQueryEvaluatorAgent()
    user_message = state.get("user_message")
    response = state["evaluate_sql_statement_agent"].is_query_heavy(user_message)
    if response == "YES":
        print(response)
        state["is_sql_query_heavy"] = "YES"
        print("Zapytanie jest ciężkie.")
    else:
        state["is_sql_query_heavy"] = "NO"
        print("Zapytanie nie jest ciężkie.")
    return state

def rag_node(state):
    print("Komunikacja z RAG!")
    user_message = state.get("user_message")
    rag_response = state["rag"].query(user_message)
    print("Odpowiedź RAG:", rag_response["answer"])
    return {
        "user_message": user_message,
        "rag_response": rag_response["answer"]
    }

def agent_node(state):
    print("Komunikacja z agentem!")
    if state.get("agent") is None:
        state["agent"] = SQL_Agent()
    user_message = state.get("user_message")
    agent_response = state["agent"].get_agent_response(user_message)
    print("Odpowiedź agenta:", agent_response)
    return {
        "user_message": user_message,
        "agent_response": agent_response,
    }
def create_rag(state):
    print("Tworzenie RAG!")
    print("Tworzę nowy RAG...")
    
    conn = sqlite3.connect(os.environ.get("transations_db"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM all_transactions")
    rows = cursor.fetchall()
    conn.close()
    print("Pobrano transakcji:", len(rows))
    if rows:
        all_text = "\n".join([str(item) for item in rows])
        docs = [Document(page_content=all_text)]
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
        llm = state["evaluate_sql_statement_agent"].llm
        state["rag"] = AdaptiveRAG(llm, retriever, vectorstore)
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