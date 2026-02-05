from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    runpod_project_id: str
    runpod_api_key: str

    gemini_api_key: str

    deepinfra_api_key: str

    pinecone_api_key: str
    pinecone_index_name: str = "house-md-medicine-wiki-articles"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )

@cache
def get_settings() -> Settings:
    # This is fine to ignore since it'll set the settings from the .env file
    settings = Settings() # type: ignore
    return settings