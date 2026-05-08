import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Semantic-Aware File Converter with Automatic Documentation Generation Using Local LLM"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LLM_PROVIDER: str = "ollama"  # Options 'ollama' or 'dummy'
    OLLAMA_MODEL: str = "llama3.2" # Adjust according to the local model you have

    class Config:
        env_file = ".env"

settings = Settings()
