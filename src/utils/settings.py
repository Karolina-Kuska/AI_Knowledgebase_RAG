from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Azure SQL
    AZURE_SQL_SERVER: str
    AZURE_SQL_DATABASE: str
    AZURE_SQL_USERNAME: str
    AZURE_SQL_PASSWORD: str
    AZURE_SQL_ENCRYPT: bool = True

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = "2024-06-01"
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-4.1-mini"
    AZURE_OPENAI_EMBED_DEPLOYMENT: str | None = None
    FORCE_LOCAL: bool = False
    # Lokalny Vector DB
    CHROMA_DIR: str = "storage/chroma"

    # Local LLM Fallback
    OLLAMA_HOST: str | None = None
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_EMBED_MODEL: str | None = None
    
    API_KEY: str | None = None
    class Config:
        env_file = ".env"
    
settings = Settings()
