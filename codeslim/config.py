"""Configuration management via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CodeSlimConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    llm_provider: str = "ollama"
    llm_model_analysis: str = "qwen2.5-coder:3b"
    llm_model_optimization: str = "qwen2.5-coder:3b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_fallback: str = "qwen2.5-coder:3b"
    groq_api_key: str | None = None
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> CodeSlimConfig:
    return CodeSlimConfig()
