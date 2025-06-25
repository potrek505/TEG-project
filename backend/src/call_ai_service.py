import os
import sys

# Dodaj ścieżkę do głównego katalogu projektu przed importami
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
from config.logging import get_logger

logger = get_logger(__name__)

def call_ai_service(endpoint, data, config=None):
    """
    Wywołuje usługę AI z właściwą obsługą błędów i konfiguracją
    """
    # Get AI service configuration
    if config:
        ai_service_url = config.get('url', os.getenv("AI_SERVICE_URL"))
        timeout = config.get('timeout', 60)
        max_retries = config.get('max_retries', 3)
        retry_delay = config.get('retry_delay', 2)
    else:
        ai_service_url = os.getenv("AI_SERVICE_URL")
        timeout = 60
        max_retries = 3
        retry_delay = 2
    
    if not ai_service_url:
        logger.error("AI service URL not configured")
        return {"error": "AI service configuration missing"}
    
    # Remove any trailing slash
    ai_service_url = ai_service_url.rstrip('/')
        
    try:
        if endpoint == 'clear':
            logger.info("Calling AI service to clear conversation")
            response = requests.post(f"{ai_service_url}/clear", json={}, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        elif endpoint == 'chat':
            message = data.get('message', '')
            session_id = data.get('session_id')
            
            if not message.strip():
                logger.warning("Empty message sent to AI service")
                return {"error": "Message cannot be empty"}
            
            logger.info(f"Sending chat message to AI service for session {session_id[:8] if session_id else 'unknown'}")
            
            # Retry logic
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        f"{ai_service_url}/chat",
                        json={"message": message, "session_id": session_id},
                        timeout=timeout
                    )
                    
                    response.raise_for_status()
                    
                    response_data = response.json()
                    
                    return {
                        "response": response_data.get("response"),
                        "session_id": session_id
                    }
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"AI service request failed (attempt {attempt + 1}), retrying in {retry_delay}s: {str(e)}")
                        import time
                        time.sleep(retry_delay)
                    else:
                        raise
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

def change_ai_provider(provider, config=None):
    """
    Zmień providera AI (OpenAI/Gemini)
    """
    # Get AI service configuration
    if config:
        ai_service_url = config.get('url', os.getenv("AI_SERVICE_URL"))
        timeout = config.get('timeout', 60)
    else:
        ai_service_url = os.getenv("AI_SERVICE_URL")
        timeout = 60
    
    if not ai_service_url:
        logger.error("AI service URL not configured")
        return {"error": "AI service configuration missing"}
    
    # Remove any trailing slash
    ai_service_url = ai_service_url.rstrip('/')
        
    try:
        logger.info(f"Changing AI provider to: {provider}")
        response = requests.post(
            f"{ai_service_url}/config/provider", 
            json={"provider": provider}, 
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            logger.info(f"Successfully changed AI provider to: {provider}")
        else:
            logger.error(f"Failed to change AI provider: {result.get('error')}")
        
        return result
        
    except requests.exceptions.Timeout:
        logger.error("Timeout when changing AI provider")
        return {"error": "AI service timeout - please try again"}
    except requests.exceptions.ConnectionError:
        logger.error("Connection error when changing AI provider")
        return {"error": "Cannot connect to AI service"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error when changing AI provider: {str(e)}")
        return {"error": f"AI service communication error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error when changing AI provider: {str(e)}")
        return {"error": "Unexpected AI service error"}