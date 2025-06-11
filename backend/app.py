from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from src.openai_service import OpenAIService

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
default_temperature = os.getenv("DEFAULT_TEMPERATURE", 0)

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

openai_service = OpenAIService(
    api_key=API_KEY,
    default_model=default_model,
    default_temperature=float(default_temperature),
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request, 'message' field is required"}), 400
    
    human_message = data.get("message")
    system_message = data.get("context", "")
    model = data.get("model", default_model)
    temperature = data.get("temperature", default_temperature)

    response = openai_service.get_response(
        human_message=human_message,
        system_message=system_message,
        model=model,
        temperature=temperature
    )

    if response:
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "Failed to get response from OpenAI"}), 500

@app.route('/api/agent-chat', methods=['POST'])
def agent_chat():
    data = request.json
    
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request, 'message' field is required"}), 400
        
    if not openai_service.supabase_client:
        return jsonify({"error": "Supabase client not configured. Please check your environment variables."}), 501
    
    human_message = data.get("message")
    system_message = data.get("context", "")
    model = data.get("model", default_model)
    temperature = data.get("temperature", default_temperature)

    response = openai_service.get_agent_response(
        human_message=human_message,
        system_message=system_message,
        model=model,
        temperature=temperature
    )

    if response:
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "Failed to get response from agent"}), 502

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/clear-conversation', methods=['POST'])
def clear_conversation():
    try:
        if hasattr(openai_service, 'clear_conversation'):
            openai_service.clear_conversation()
        return jsonify({
            "status": "success", 
            "message": "Conversation memory cleared successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to clear conversation: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to clear conversation: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=55000, debug=True)