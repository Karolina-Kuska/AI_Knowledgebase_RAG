from langchain_chroma import Chroma

from src.rag.provider import get_embeddings
from src.utils.settings import settings
import os

def get_chroma():
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
    return Chroma(
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_DIR,  
        collection_name="kb_articles",
    )