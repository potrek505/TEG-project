from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
from src.graphs.dynamic_rag_graph import get_dynamic_rag_graph

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging import init_logging, get_logger

# Import config manager - lokalny import w kontenerze
from config.config_manager import get_ai_config

# Inicjalizacja systemu logowania
init_logging()
logger = get_logger(__name__)

# Initialize config manager
config_manager = get_ai_config()

load_dotenv()

app = Flask(__name__)

# Configure Flask app with config manager
server_config = config_manager.get("server")
app.config.update({
    'DEBUG': server_config.get('debug', False) if server_config else False
})

try:
    # Get RAG configuration
    rag_enabled = config_manager.get("rag", "enabled", default=True)
    logger.info(f"RAG configuration loaded: enabled={rag_enabled}")
    
    if rag_enabled:
        graph = get_dynamic_rag_graph()
        logger.info("Dynamic RAG graph initialized successfully")
    else:
        graph = None
        logger.info("RAG disabled in configuration")
except Exception as e:
    logger.error(f"Failed to initialize RAG graph: {str(e)}")
    graph = None

session_states = {}

# Configuration endpoint
@app.route('/config', methods=['GET'])
def get_config():
    """Get current AI configuration."""
    try:
        return jsonify({
            "success": True,
            "data": {
                "llm": config_manager.get("llm", default={}),
                "rag": config_manager.get("rag", default={}),
                "server": config_manager.get("server", default={})
            }
        })
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config/reload', methods=['POST'])
def reload_config():
    """Reload AI configuration."""
    try:
        config_manager.reload_config()
        logger.info("AI configuration reloaded")
        return jsonify({"success": True, "message": "Configuration reloaded"})
    except Exception as e:
        logger.error(f"Error reloading config: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with configuration status."""
    graph_status = "healthy" if graph else "unhealthy"
    rag_enabled = config_manager.get("rag", "enabled", default=True)
    
    return jsonify({
        "status": "healthy", 
        "service": "ai",
        "graph": graph_status,
        "rag_enabled": rag_enabled,
        "config_loaded": True,
        "llm_provider": config_manager.get("llm", "provider", default="openai"),
        "llm_model": config_manager.get("llm", "model", default="gpt-4o-mini")
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

@app.route('/config/provider', methods=['POST'])
def change_provider():
    """Change AI provider (OpenAI/Gemini)."""
    try:
        data = request.get_json()
        if not data or 'provider' not in data:
            return jsonify({"success": False, "error": "Provider not specified"}), 400
        
        provider = data['provider'].lower()
        if provider not in ['openai', 'gemini']:
            return jsonify({"success": False, "error": "Invalid provider. Use 'openai' or 'gemini'"}), 400
        
        # Update configuration
        config_manager.set("llm", "provider", provider)
        
        # Set model based on provider
        if provider == 'gemini':
            model = config_manager.get("google_llm", "model", default="gemini-2.5-flash")
            temp = config_manager.get("google_llm", "temperature", default=0.7)
            config_manager.set("llm", "provider", "gemini")
            config_manager.set("llm", "model", model)
            config_manager.set("llm", "temperature", temp)
        else:  # openai
            model = config_manager.get("openai_llm", "model", default="gpt-4o-mini")
            temp = config_manager.get("openai_llm", "temperature", default=0.7)
            config_manager.set("llm", "provider", "openai")
            config_manager.set("llm", "model", model)
            config_manager.set("llm", "temperature", temp)
        
        # Save configuration
        config_manager.save_config()
        
        # Clear session states to force recreation of agents with new provider
        global session_states
        session_states.clear()
        logger.info("Session states cleared - agents will be recreated with new provider")
        
        logger.info(f"AI provider changed to: {provider}")
        return jsonify({
            "success": True, 
            "message": f"Provider changed to {provider}. All sessions cleared.",
            "current_config": {
                "provider": config_manager.get("llm", "provider"),
                "model": config_manager.get("llm", "model"),
                "temperature": config_manager.get("llm", "temperature")
            }
        })
    except Exception as e:
        logger.error(f"Error changing provider: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

def update_env_file(key, value):
    """Update or add a key-value pair in the .env file."""
    try:
        env_file_path = config_manager.env_file
        lines = []
        key_found = False
        
        # Read existing lines if file exists
        if env_file_path.exists():
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
        
        # Update existing key or mark that it wasn't found
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}=") or line.strip().startswith(f"#{key}="):
                lines[i] = f"{key}={value}\n"
                key_found = True
                break
        
        # Add key if not found
        if not key_found:
            lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_file_path, 'w') as f:
            f.writelines(lines)
            
        # Update environment variable for current session
        os.environ[key] = value
        
        logger.info(f"Updated .env file: {key}={value}")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        # Get server configuration from config manager
        server_config = config_manager.get_server_config()
        
        # Pobierz port z argumentów uruchomieniowych, config managera lub os.getenv
        import argparse
        parser = argparse.ArgumentParser(description="Start AI service")
        parser.add_argument('--port', type=int, help="Port to run the AI service on")
        args = parser.parse_args()

        port = (args.port if args.port 
                else server_config.get('port', int(os.getenv('AI_PORT', 5001))))
        host = server_config.get('host', '0.0.0.0')
        debug = server_config.get('debug', False)
        
        logger.info(f"Starting AI service on {host}:{port} (debug={debug})")
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("AI service stopped by user")
    except Exception as e:
        logger.error(f"Failed to start AI service: {str(e)}")
        sys.exit(1)
    finally:
        # Stop config manager watching
        config_manager.stop_watching()