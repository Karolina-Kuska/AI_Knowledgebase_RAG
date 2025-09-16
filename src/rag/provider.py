from src.utils.settings import settings
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from typing import Optional
try:
    from langchain_ollama import ChatOllama
except Exception:
    ChatOllama = None   

def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_EMBED_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
    )

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        temperature=0.2,
        timeout=20,
    )

def get_local_llm():
    if not settings.OLLAMA_HOST:
        return None
    return ChatOllama(
        base_url=settings.OLLAMA_HOST,
        model=settings.OLLAMA_MODEL or "gemma3:4b",
        temperature=0.2,
    )
