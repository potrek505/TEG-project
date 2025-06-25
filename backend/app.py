import os
import uuid
import sys
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from src.call_ai_service import call_ai_service
from src.database import ConversationDB

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging import init_logging, get_logger

# Import config manager - lokalny import w kontenerze
from config.config_manager import get_backend_config

# Inicjalizacja systemu logowania
init_logging()
logger = get_logger(__name__)

# Initialize config manager
config_manager = get_backend_config()

load_dotenv()

app = Flask(__name__)

# Configure Flask app with config manager
server_config = config_manager.get("server")
app.config.update({
    'DEBUG': server_config.get('debug', False) if server_config else False
})

try:
    # Get database configuration
    db_config = config_manager.get("database")
    conversations_path = db_config.get('conversations_path', './conversations.db') if db_config else './conversations.db'
    logger.info(f"Database configuration loaded: {conversations_path}")
    
    db = ConversationDB()
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    db = None

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with configuration status."""
    db_status = "healthy" if db else "unhealthy"
    ai_service_config = config_manager.get("ai_service")
    
    return jsonify({
        "status": "healthy", 
        "service": "backend",
        "database": db_status,
        "config_loaded": True,
        "ai_service_url": ai_service_config.get('url', 'http://ai:5001') if ai_service_config else 'http://ai:5001'
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not db:
            logger.error("Database not available")
            return jsonify({"error": "Database service unavailable"}), 503
            
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received in chat request")
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message or not message.strip():
            logger.warning(f"Empty message received from session {session_id}")
            return jsonify({"error": "Message is required and cannot be empty"}), 400
        
        # Get AI service configuration
        ai_service_config = config_manager.get("ai_service")
        
        logger.info(f"Processing chat message for session {session_id[:8]}...")
        
        ai_response = call_ai_service('chat', {
            "message": message,
            "session_id": session_id
        }, config=ai_service_config)
        
        if "error" in ai_response:
            logger.error(f"AI service error: {ai_response['error']}")
            return jsonify(ai_response), 501
        
        response_text = ai_response.get("response")
        if not response_text:
            logger.warning("AI service returned empty response")
            return jsonify({"error": "Empty response from AI service"}), 502
        
        try:
            db.save_conversation(session_id, message, response_text)
            logger.info(f"Conversation saved for session {session_id[:8]}")
        except Exception as db_error:
            logger.error(f"Failed to save conversation: {str(db_error)}")
            # Kontynuuj mimo błędu zapisu do bazy
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/clear-conversation', methods=['POST'])
def clear_conversation():
    """Czyści pamięć konwersacji i zapisuje aktualną sesję do bazy"""
    try:
        logger.info("Clearing conversation memory...")
        
        clear_response = call_ai_service('clear', {})
        
        if "error" in clear_response:
            logger.error(f"Failed to clear conversation: {clear_response['error']}")
            return jsonify({
                "status": "error", 
                "message": f"Failed to clear conversation: {clear_response['error']}"
            }), 511
        
        logger.info("Conversation memory cleared successfully")
        return jsonify({
            "status": "success", 
            "message": "Conversation memory cleared successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to clear conversation: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to clear conversation due to internal error"
        }), 510

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Pobiera historię konwersacji"""
    try:
        if not db:
            logger.error("Database not available for conversations request")
            return jsonify({"error": "Database service unavailable"}), 503
            
        session_id = request.args.get('session_id')
        logger.info(f"Fetching conversations for session: {session_id[:8] if session_id else 'all'}")
        
        conversations = db.get_conversation_history(session_id)
        return jsonify({
            "conversations": conversations,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return jsonify({"error": "Failed to fetch conversations"}), 520

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Pobiera wszystkie sesje"""
    try:
        if not db:
            logger.error("Database not available for sessions request")
            return jsonify({"error": "Database service unavailable"}), 503
            
        logger.info("Fetching all sessions")
        sessions = db.get_all_sessions()
        return jsonify({
            "sessions": sessions,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        return jsonify({"error": "Failed to fetch sessions"}), 530

@app.route('/conversations/reset', methods=['POST'])
def reset_conversation():
    """Tworzy nową sesję"""
    try:
        new_session_id = str(uuid.uuid4())
        logger.info(f"Created new session: {new_session_id[:8]}")
        
        return jsonify({
            "session_id": new_session_id,
            "status": "success",
            "message": "New conversation session created"
        })
    except Exception as e:
        logger.error(f"Error creating new session: {str(e)}")
        return jsonify({"error": "Failed to create new session"}), 540
    
@app.route('/conversations/reset-database', methods=['POST'])
def reset_database():
    """Usuwa wszystkie dane z bazy danych"""
    try:
        if not db:
            logger.error("Database not available for reset request")
            return jsonify({
                "status": "error", 
                "message": "Database service unavailable"
            }), 503
            
        logger.warning("Resetting entire database - all data will be deleted")
        result = db.clear_all_data()
        if result:
            logger.info("Database reset completed successfully")
            return jsonify({
                "status": "success", 
                "message": "All database records have been deleted"
            }), 200
        else:
            logger.error("Database reset failed")
            return jsonify({
                "status": "error", 
                "message": "Failed to delete database records"
            }), 551
            
    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to reset database due to internal error"
        }), 550

# Configuration endpoints
@app.route('/config', methods=['GET'])
def get_backend_config():
    """Get current backend configuration with AI status."""
    try:
        # Get backend config
        backend_data = {
            "server": config_manager.get("server", default={}),
            "ai_service": config_manager.get("ai_service", default={}),
            "database": config_manager.get("database", default={}),
            "cors": config_manager.get("cors", default={}),
            "security": config_manager.get("security", default={})
        }
        
        # Try to get AI config as well
        try:
            ai_service_config = config_manager.get("ai_service")
            ai_service_url = ai_service_config.get('url', os.getenv("AI_SERVICE_URL", "http://localhost:50001"))
            ai_service_url = ai_service_url.rstrip('/')
            
            ai_response = requests.get(f"{ai_service_url}/config", timeout=5)
            if ai_response.status_code == 200:
                ai_config = ai_response.json()
                # Add AI config to response
                backend_data["ai_current"] = ai_config.get("data", {})
        except Exception as ai_error:
            logger.warning(f"Could not fetch AI config: {str(ai_error)}")
            backend_data["ai_current"] = {}
        
        return jsonify({
            "success": True,
            "data": backend_data
        })
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config/reload', methods=['POST'])
def reload_backend_config():
    """Reload backend configuration."""
    try:
        config_manager.reload_config()
        logger.info("Backend configuration reloaded")
        return jsonify({"success": True, "message": "Configuration reloaded"})
    except Exception as e:
        logger.error(f"Error reloading config: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config/ai-provider', methods=['POST'])
def change_ai_provider():
    """Change AI provider (OpenAI/Gemini)."""
    try:
        data = request.get_json()
        if not data or 'provider' not in data:
            return jsonify({"success": False, "error": "Provider not specified"}), 400
        
        provider = data['provider'].lower()
        if provider not in ['openai', 'gemini']:
            return jsonify({"success": False, "error": "Invalid provider. Use 'openai' or 'gemini'"}), 400
        
        # Get AI service configuration
        ai_service_config = config_manager.get("ai_service")
        
        # Call AI service to change provider
        from src.call_ai_service import change_ai_provider
        result = change_ai_provider(provider, config=ai_service_config)
        
        if result.get("success"):
            logger.info(f"AI provider changed to: {provider}")
            return jsonify(result)
        else:
            logger.error(f"Failed to change AI provider: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error changing AI provider: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config/ai', methods=['GET'])
def get_ai_config():
    """Get AI configuration from AI service."""
    try:
        # Get AI service configuration
        ai_service_config = config_manager.get("ai_service")
        ai_service_url = ai_service_config.get('url', os.getenv("AI_SERVICE_URL", "http://localhost:50001"))
        
        # Remove any trailing slash
        ai_service_url = ai_service_url.rstrip('/')
        
        response = requests.get(f"{ai_service_url}/config", timeout=10)
        if response.status_code == 200:
            ai_config = response.json()
            return jsonify(ai_config)
        else:
            logger.error(f"Failed to fetch AI config. Status: {response.status_code}")
            return jsonify({"success": False, "error": "Failed to fetch AI config"}), 500
            
    except Exception as e:
        logger.error(f"Error fetching AI config: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    try:
        # Pobierz port z argumentów uruchomieniowych lub z os.getenv
        import argparse
        parser = argparse.ArgumentParser(description="Start backend server")
        parser.add_argument('--port', type=int, help="Port to run the backend server on")
        args = parser.parse_args()

        port = args.port if args.port else int(os.getenv('BACKEND_PORT', 5000))
        logger.info(f"Starting backend server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start backend server: {str(e)}")
        sys.exit(1)