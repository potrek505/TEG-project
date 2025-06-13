from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.openai_service import OpenAIService

load_dotenv()

app = Flask(__name__)


ai_service = OpenAIService(
    api_key=os.environ.get('OPENAI_API_KEY'),
    default_model=os.environ.get('DEFAULT_MODEL', 'gpt-4o-mini'),
    default_temperature=float(os.environ.get('DEFAULT_TEMPERATURE', 0.7)),
    supabase_url=os.environ.get('SUPABASE_URL'),
    supabase_key=os.environ.get('SUPABASE_KEY')
)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "ai"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "Message is required"}), 410
        
        response = ai_service.get_agent_response(message)
        
        return jsonify({
            "response": response,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 560

@app.route('/clear', methods=['POST'])
def clear_conversation():
    try:
        ai_service.clear_conversation()
        return jsonify({"status": "conversation cleared", "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 570

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('AI_PORT')), debug=True)