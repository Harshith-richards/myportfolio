"""Configuration models for NEXUS."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QueueMode(str, Enum):
    """Execution queue mode."""

    ASYNCIO = "asyncio"
    CELERY = "celery"


class MemoryBackend(str, Enum):
    """Long-term memory backend type."""

    CHROMA = "chromadb"
    FAISS = "faiss"
    PINECONE = "pinecone"


class AgentConfig(BaseSettings):
    """Runtime configuration for orchestrator and agents."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "NEXUS"
    environment: Literal["dev", "test", "prod"] = "dev"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    default_provider: str = "openai"
    default_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    queue_mode: QueueMode = QueueMode.ASYNCIO
    redis_url: str = "redis://localhost:6379/0"
    sqlite_path: str = "nexus.db"
    postgres_dsn: str = ""
    memory_backend: MemoryBackend = MemoryBackend.CHROMA
    chroma_path: Path = Field(default=Path(".nexus/chroma"))
    max_iterations: int = 10
    max_llm_calls: int = 200
    session_cost_budget_usd: float = 10.0
    human_in_loop: bool = False
    permission_level: str = "STANDARD"
    allowed_file_roots: list[str] = Field(default_factory=lambda: [".", "workspace", "tmp"])


settings = AgentConfig()
