import requests
import os

def call_ai_service(endpoint, data):
    """Call AI service via HTTP"""
    try:
        ai_service_url = os.environ.get('AI_SERVICE_URL', f'http://localhost:{os.environ.get("AI_PORT")}')
        response = requests.post(f"{ai_service_url}/{endpoint}", json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"AI service error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"AI service unavailable: {str(e)}"}