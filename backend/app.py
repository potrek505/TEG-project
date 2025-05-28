from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from src.openai_service import OpenAIService

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
openai_service = OpenAIService(api_key=API_KEY)

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
default_temperature = os.getenv("DEFAULT_TEMPERATURE", 0.7)

openai_service = OpenAIService(
    api_key=API_KEY,
    default_model=default_model,
    default_temperature=float(default_temperature)
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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=55000, debug=True)