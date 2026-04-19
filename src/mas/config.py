from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for local MAS execution."""

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    reports_dir: str = os.getenv("REPORTS_DIR", "reports")
    logs_dir: str = os.getenv("LOGS_DIR", "logs")
    offline_mode: bool = os.getenv("MAS_OFFLINE_MODE", "0") == "1"


settings = Settings()
