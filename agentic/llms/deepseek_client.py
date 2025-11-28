from langchain_deepseek import ChatDeepSeek
from ...core.config import settings

def get_deepseek_chat()-> ChatDeepSeek:
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=settings.DEEPSEEK_API_KEY,
        )