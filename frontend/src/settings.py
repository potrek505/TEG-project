import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'app': {
        'title': "Your Finance Buddy",
        'layout': "wide"
    },
    'backend_url': os.getenv("BACKEND_SERVICE_URL"),
    'default_system_message': "You are Your Finance Buddy, a helpful and knowledgeable financial advisor AI assistant. Provide accurate financial guidance, investment advice, budgeting tips, and money management strategies in a friendly and approachable manner.",
    'chat_placeholder': "Ask Your Finance Buddy anything about money...",
    'app_title': "Your Finance Buddy"
}