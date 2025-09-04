from langchain_openai import ChatOpenAI
# from ...core.config import settings


def get_openai_client() -> ChatOpenAI:
    """Return a configured OpenAI client."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.6,
        top_p=0.8,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=settings.OPENAI_API_KEY,
    )