from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from ai.src.agents.SQL_Agent import OpenAIService
import os
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict):
    graph_state: str
    rag: object | None
    agent: object | None
    user_message: str | None
    agent_response: str | None
    rag_response: str | None

def node_1(state):
    print("--- Node 1 ---")
    if state.get("rag") is not None:
        print("RAG istnieje! Przechodzę do rag_node.")
    else:
        print("RAG nie istnieje! Przechodzę do agent_node.")
    return state

def rag_node(state):
    print("Komunikacja z RAG!")
    rag = state["rag"]
    user_message = state.get("user_message", "Cześć, opowiedz mi o moich transakcjach.")
    if rag:
        rag_response = rag.query(user_message)
        print("Odpowiedź RAG:", rag_response["answer"])
        return {
            "graph_state": state['graph_state'] + " [RAG]",
            "rag": rag,
            "agent": state["agent"],
            "user_message": user_message,
            "agent_response": state.get("agent_response"),
            "rag_response": rag_response["answer"]
        }
    else:
        print("Brak RAG w stanie!")
        return state

def agent_node(state):
    print("Komunikacja z agentem!")
    agent = state["agent"]
    if agent:
        user_message = state.get("user_message", "Cześć, opowiedz mi o moich transakcjach.")
        response = agent.get_agent_response(user_message)
        print("Odpowiedź agenta:", response)

        # Oczekujemy, że response to dict {"answer": ..., "data": [...]}
        if isinstance(response, dict):
            answer = response.get("answer", "")
            data = response.get("data", [])
        else:
            # fallback na stary format
            import json
            try:
                parsed = json.loads(response)
                answer = parsed.get("answer", "")
                data = parsed.get("data", [])
            except Exception:
                answer = str(response)
                data = []

        # Tworzymy RAG tylko jeśli są dane
        rag = None
        if data:
            from langchain_core.documents import Document
            docs = [Document(page_content=str(item)) for item in data]

            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever = vectorstore.as_retriever()

            from src.rags.advanced_rag_config import AdaptiveRAG
            llm = agent.llm
            rag = AdaptiveRAG(llm, retriever, vectorstore)

        return {
            "graph_state": state['graph_state'] + " [AGENT->RAG]",
            "rag": rag,
            "agent": agent,
            "user_message": user_message,
            "agent_response": answer,   # <-- to zwracaj użytkownikowi!
            "rag_response": None
        }
    else:
        print("Brak agenta w stanie!")
        return state

builder = StateGraph(State)
builder.add_node("Node1", node_1)
builder.add_node("RAG", rag_node)
builder.add_node("AGENT", agent_node)

builder.add_edge(START, "Node1")
builder.add_conditional_edges("Node1", lambda state: "RAG" if state.get("rag") is not None else "create_sql_statement")
builder.add_edge("create_sql_statement", "evaluate_sql_statement")
builder.add_conditional_edges("evaluate_sql_statement", lambda state: "create_rag" if state.get("rag") is not None else "unnecessary")
builder.add_edge("create_rag", "RAG")
builder.add_edge("RAG", END)
builder.add_edge("unnecessary", END)

#graph = builder.compile()

agent_instance = OpenAIService(
    api_key=os.environ.get('OPENAI_API_KEY'),
    default_model=os.environ.get('DEFAULT_MODEL', 'gpt-4o-mini'),
    default_temperature=float(os.environ.get('DEFAULT_TEMPERATURE', 0.7)),
    supabase_url=os.environ.get('SUPABASE_URL'),
    supabase_key=os.environ.get('SUPABASE_KEY')
)
