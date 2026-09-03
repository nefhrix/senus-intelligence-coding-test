from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "Senus Board Intelligence"

    database_url: str = "sqlite:///./senus.db"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    mineru_api_url: str = "http://127.0.0.1:8001"

    upload_dir: str = "uploads"

    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()