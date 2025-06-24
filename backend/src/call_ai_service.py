import os
import sys
import requests

# Import shared logging system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared_logging import get_logger

logger = get_logger(__name__)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")

def call_ai_service(endpoint, data):
    """
    Wywołuje usługę AI z właściwą obsługą błędów
    """
    if not AI_SERVICE_URL:
        logger.error("AI_SERVICE_URL not configured")
        return {"error": "AI service configuration missing"}
        
    try:
        if endpoint == 'clear':
            logger.info("Calling AI service to clear conversation")
            response = requests.post(f"{AI_SERVICE_URL}/clear", json={}, timeout=30)
            response.raise_for_status()
            return response.json()
            
        elif endpoint == 'chat':
            message = data.get('message', '')
            session_id = data.get('session_id')
            
            if not message.strip():
                logger.warning("Empty message sent to AI service")
                return {"error": "Message cannot be empty"}
            
            logger.info(f"Sending chat message to AI service for session {session_id[:8] if session_id else 'unknown'}")
            
            response = requests.post(
                f"{AI_SERVICE_URL}/chat",
                json={"message": message, "session_id": session_id},
                timeout=60
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                "response": response_data.get("response"),
                "session_id": session_id
            }
        else:
            logger.error(f"Unknown endpoint: {endpoint}")
            return {"error": f"Unknown endpoint: {endpoint}"}
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout when calling AI service endpoint: {endpoint}")
        return {"error": "AI service timeout - please try again"}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error when calling AI service endpoint: {endpoint}")
        return {"error": "Cannot connect to AI service"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error when calling AI service: {str(e)}")
        return {"error": f"AI service communication error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error when calling AI service: {str(e)}")
        return {"error": "Unexpected AI service error"}