from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.1-8b-instruct"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    superhero_api_token: str = ""
    superhero_base_url: str = "https://www.superheroapi.com/api"
    request_timeout_seconds: float = 45.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
