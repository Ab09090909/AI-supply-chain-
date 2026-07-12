"""
Producer Chatbot Engine
Wrapper for AI assistant
"""
from producer.ai_assistant.chat import AIAssistant, assistant

def get_chatbot_response(message: str) -> str:
    """Get response from chatbot"""
    return assistant._generate_response(message)

def render_chat():
    """Render chat interface"""
    assistant.render()
