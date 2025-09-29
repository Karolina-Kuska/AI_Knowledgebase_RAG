from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from src.utils.settings import settings

def get_chroma():
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_EMBED_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
    )
    return Chroma(
        persist_directory="chroma_db",
        collection_name="kb_articles",
        embedding_function=embeddings  
    )
