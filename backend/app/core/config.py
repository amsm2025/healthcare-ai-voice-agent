from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare AI Voice Agent"
    app_env: str = "development"

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    calcom_api_key: str = ""
    calcom_event_type_id: str = ""
    calcom_base_url: str = "https://api.cal.com"

    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
