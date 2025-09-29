from typing import Tuple, Optional
from src.utils.settings import settings
from langchain_openai import AzureChatOpenAI, ChatOpenAI, AzureOpenAIEmbeddings

try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
except Exception:
    ChatOllama = None
    OllamaEmbeddings = None

def _has_azure_env() -> bool:
    return all([
        settings.AZURE_OPENAI_ENDPOINT,
        settings.AZURE_OPENAI_API_KEY,
        settings.AZURE_OPENAI_API_VERSION,
        settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
    ])

def _make_azure_llm(timeout: int = 20):
    return AzureChatOpenAI(
        azure_deployment=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        timeout=timeout,
    )

def _make_ollama_llm(timeout: int = 20):
    if settings.OLLAMA_HOST and ChatOllama is not None:
        return ChatOllama(
            base_url=settings.OLLAMA_HOST,
            model=(settings.OLLAMA_MODEL or "llama3.1"),
        )
    if settings.OLLAMA_HOST:
        return ChatOpenAI(
            model=(settings.OLLAMA_MODEL or "llama3.1"),
            openai_api_key="ollama",               # placeholder
            base_url=f"{settings.OLLAMA_HOST}/v1",
            timeout=timeout,
        )
    return None

def get_llm(timeout: int = 20):
    if _has_azure_env() and not getattr(settings, "FORCE_LOCAL", False):
        try:
            return _make_azure_llm(timeout)
        except Exception:
            pass

    llm = _make_ollama_llm(timeout)
    if llm is not None:
        return llm

    raise RuntimeError("Brak dostępnego LLM (Azure/Ollama).")

def get_llm_with_name(timeout: int = 20) -> Tuple[object, str]:
    if _has_azure_env() and not getattr(settings, "FORCE_LOCAL", False):
        try:
            return _make_azure_llm(timeout), "azure-openai"
        except Exception:
            pass

    if settings.OLLAMA_HOST and ChatOllama is not None:
        return _make_ollama_llm(timeout), "ollama"

    if settings.OLLAMA_HOST:
        return _make_ollama_llm(timeout), "ollama-openai-compatible"

    raise RuntimeError("Brak dostępnego LLM (Azure/Ollama).")

def get_local_llm() -> Optional[object]:

    return _make_ollama_llm()

def _has_azure_embed_env() -> bool:
    return all([
        settings.AZURE_OPENAI_ENDPOINT,
        settings.AZURE_OPENAI_API_KEY,
        settings.AZURE_OPENAI_API_VERSION,
        getattr(settings, "AZURE_OPENAI_EMBED_DEPLOYMENT", None),
    ])

_EMBEDDINGS_CACHE: Optional[object] = None
_EMBED_ENGINE: Optional[str] = None  # 'azure-openai' | 'ollama'

def get_embeddings():
    global _EMBEDDINGS_CACHE, _EMBED_ENGINE
    if _EMBEDDINGS_CACHE is not None:
        return _EMBEDDINGS_CACHE

    if _has_azure_embed_env() and not getattr(settings, "FORCE_LOCAL", False):
        try:
            emb = AzureOpenAIEmbeddings(
                azure_deployment=settings.AZURE_OPENAI_EMBED_DEPLOYMENT,
                openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
            )
            _ = emb.embed_query("healthcheck")
            _EMBEDDINGS_CACHE = emb
            _EMBED_ENGINE = "azure-openai"
            return _EMBEDDINGS_CACHE
        except Exception:
            pass

    if settings.OLLAMA_HOST and OllamaEmbeddings is not None:
        emb = OllamaEmbeddings(
            base_url=settings.OLLAMA_HOST,
            model=(getattr(settings, "OLLAMA_EMBED_MODEL", None) or "nomic-embed-text")
        )
        _EMBEDDINGS_CACHE = emb
        _EMBED_ENGINE = "ollama"
        return _EMBEDDINGS_CACHE

    raise RuntimeError("Brak dostępnych embeddingów (Azure/Ollama).")
