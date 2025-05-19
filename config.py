from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    azure_openai_api_type: str = os.getenv("AZURE_OPENAI_API_TYPE", "azure")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()