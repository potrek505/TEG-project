from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
from src.graphs.dynamic_rag_graph import get_dynamic_rag_graph

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_logging import setup_logging

# Konfiguracja loggera używając shared_logging
logger = setup_logging("ai")

load_dotenv()

app = Flask(__name__)

try:
    graph = get_dynamic_rag_graph()
    logger.info("Dynamic RAG graph initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG graph: {str(e)}")
    graph = None

session_states = {}

@app.route('/health', methods=['GET'])
def health_check():
    graph_status = "healthy" if graph else "unhealthy"
    return jsonify({
        "status": "healthy", 
        "service": "ai",
        "graph": graph_status
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not graph:
            logger.error("RAG graph not available")
            return jsonify({"error": "AI service not properly initialized"}), 503
            
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received in chat request")
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        
        if not message or not message.strip():
            logger.warning(f"Empty message received from session {session_id}")
            return jsonify({"error": "Message is required and cannot be empty"}), 410

        logger.info(f"Processing message for session {session_id}")

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
        try:
            new_state = graph.invoke(prev_state)
            session_states[session_id] = new_state
            
            response = new_state.get("rag_response") or new_state.get("agent_response") or "Brak odpowiedzi"
            logger.info(f"Generated response for session {session_id}")
            
            return jsonify({"response": response, "status": "success"})
            
        except Exception as graph_error:
            logger.error(f"Error processing graph for session {session_id}: {str(graph_error)}")
            return jsonify({"error": "Failed to process request"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        logger.info(f"Clear called for session_id: {session_id}")
        
        # Usuń stan tej sesji jeśli istnieje
        if session_id in session_states:
            del session_states[session_id]
            logger.info(f"Session state cleared for: {session_id}")
        else:
            logger.info(f"No session state found for: {session_id}")
            
        return jsonify({
            "status": "conversation cleared",
            "success": True,
            "session_id": session_id
        })
    except Exception as e:
        logger.error(f"/clear failed: {str(e)}")
        return jsonify({"error": "Failed to clear conversation"}), 500

if __name__ == '__main__':
    try:
        # Pobierz port z argumentów uruchomieniowych lub z os.getenv
        import argparse
        parser = argparse.ArgumentParser(description="Start AI service")
        parser.add_argument('--port', type=int, help="Port to run the AI service on")
        args = parser.parse_args()

        port = args.port if args.port else int(os.getenv('AI_PORT', 5001))
        logger.info(f"Starting AI service on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start AI service: {str(e)}")
        sys.exit(1)