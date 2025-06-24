from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.graphs.dynamic_rag_graph import get_dynamic_rag_graph

load_dotenv()

app = Flask(__name__)

graph = get_dynamic_rag_graph()
session_states = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "ai"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id', 'default')
    if not message:
        return jsonify({"error": "Message is required"}), 410

    # Pobierz poprzedni stan lub zainicjalizuj nowy
    prev_state = session_states.get(session_id, {
        "graph_state": "START",
        "rag": None,
        "sql_agent": None,
        "evaluate_sql_statement_agent": None,
        "user_message": None,
        "agent_response": None,
        "rag_response": None,
        "is_sql_query_heavy": None,
    })
    prev_state["user_message"] = message  # Aktualizuj wiadomość użytkownika

    # Przetwórz stan przez graf
    new_state = graph.invoke(prev_state)
    session_states[session_id] = new_state

    response = new_state.get("rag_response") or new_state.get("agent_response") or "Brak odpowiedzi"
    return jsonify({"response": response, "status": "success"})

@app.route('/clear', methods=['POST'])
def clear_conversation():
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        print(f"[DEBUG] Clear called for session_id: {session_id}")
        # Usuń stan tej sesji jeśli istnieje
        if session_id in session_states:
            del session_states[session_id]
        return jsonify({
            "status": "conversation cleared",
            "success": True,
            "session_id": session_id
        })
    except Exception as e:
        print(f"[ERROR] /clear failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('AI_PORT')), debug=True)