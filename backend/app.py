import os
import uuid
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from src.call_ai_service import call_ai_service
from src.database import ConversationDB

load_dotenv()

app = Flask(__name__)
db = ConversationDB()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "backend"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        ai_response = call_ai_service('chat', {
            "message": message,
            "session_id": session_id
        })
        
        if "error" in ai_response:
            return jsonify(ai_response), 501
        
        response_text = ai_response.get("response")
        
        db.save_conversation(session_id, message, response_text)
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-conversation', methods=['POST'])
def clear_conversation():
    """Czyści pamięć konwersacji i zapisuje aktualną sesję do bazy"""
    try:
        
        clear_response = call_ai_service('clear', {})
        
        if "error" in clear_response:
            return jsonify({
                "status": "error", 
                "message": f"Failed to clear conversation: {clear_response['error']}"
            }), 511
        
        return jsonify({
            "status": "success", 
            "message": "Conversation memory cleared successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to clear conversation: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to clear conversation: {str(e)}"
        }), 510

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Pobiera historię konwersacji"""
    try:
        session_id = request.args.get('session_id')
        conversations = db.get_conversation_history(session_id)
        return jsonify({
            "conversations": conversations,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 520

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Pobiera wszystkie sesje"""
    try:
        sessions = db.get_all_sessions()
        return jsonify({
            "sessions": sessions,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 530

@app.route('/conversations/reset', methods=['POST'])
def reset_conversation():
    """Tworzy nową sesję"""
    try:
        new_session_id = str(uuid.uuid4())
        
        return jsonify({
            "session_id": new_session_id,
            "status": "success",
            "message": "New conversation session created"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 540
    
@app.route('/conversations/reset-database', methods=['POST'])
def reset_database():
    """Usuwa wszystkie dane z bazy danych"""
    try:
        result = db.clear_all_data()
        if result:
            return jsonify({
                "status": "success", 
                "message": "All database records have been deleted"
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to delete database records"
            }), 551
            
    except Exception as e:
        print(f"[ERROR] Failed to reset database: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to reset database: {str(e)}"
        }), 550

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('BACKEND_PORT')), debug=True)