import os
import sys
from dotenv import load_dotenv

# Import frontend config manager
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from frontend.config.config_manager import get_frontend_config

load_dotenv()

# Initialize config manager
config_manager = get_frontend_config()

# Get configuration from config manager
app_config = config_manager.get("app", default={})
ui_config = config_manager.get("ui", default={})
backend_config = config_manager.get("backend_service", default={})

config = {
    'app': {
        'title': app_config.get('title', "Your Finance Buddy"),
        'layout': app_config.get('layout', "wide"),
        'theme': app_config.get('theme', 'light')
    },
    'backend_url': backend_config.get('url', os.getenv("BACKEND_SERVICE_URL")),
    'default_system_message': "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant.",
    'chat_placeholder': "Ask Your Finance Buddy anything about money...",
    'app_title': app_config.get('title', "Your Finance Buddy"),
    
    # Additional UI settings from config manager
    'ui': ui_config
}

def get_config():
    """Get current configuration."""
    return config

def reload_config():
    """Reload configuration from config manager."""
    global config
    config_manager.reload_config()
    
    # Update config dict
    app_config = config_manager.get("app", default={})
    ui_config = config_manager.get("ui", default={})
    backend_config = config_manager.get("backend_service", default={})
    
    config.update({
        'app': {
            'title': app_config.get('title', "Your Finance Buddy"),
            'layout': app_config.get('layout', "wide"),
            'theme': app_config.get('theme', 'light')
        },
        'backend_url': backend_config.get('url', os.getenv("BACKEND_SERVICE_URL")),
        'ui': ui_config
    })
    
    return config