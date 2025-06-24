import os
import requests

AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL')

def call_ai_service(endpoint, data):
    """
    Wywołuje usługę AI
    """
    try:
        if endpoint == 'clear':
            response = requests.post(f"{AI_SERVICE_URL}/clear", json={})
            response.raise_for_status()
            return response.json()
            
        elif endpoint == 'chat':
            message = data.get('message', '')
            session_id = data.get('session_id')
            
            response = requests.post(
                f"{AI_SERVICE_URL}/chat",
                json={"message": message}
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                "response": response_data.get("response"),
                "session_id": session_id
            }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"AI service communication error: {str(e)}"}
    except Exception as e:
        return {"error": f"AI service error: {str(e)}"}