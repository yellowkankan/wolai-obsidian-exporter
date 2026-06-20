from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    token: str
    output_dir: Path
    api_base_url: str = "https://api.wolai.com/v1/mcp"
    timeout_seconds: float = 30.0
    max_retries: int = 3


class ConfigError(RuntimeError):
    pass


def load_settings(
    output_dir: Path, token: Optional[str] = None, api_base_url: Optional[str] = None
) -> Settings:
    load_dotenv()
    resolved_token = token or os.getenv("WOLAI_TOKEN")
    if not resolved_token:
        raise ConfigError("WOLAI_TOKEN is not set. Export it in your shell or pass --token-env.")
    return Settings(
        token=resolved_token,
        output_dir=output_dir.expanduser().resolve(),
        api_base_url=api_base_url
        or os.getenv("WOLAI_API_BASE_URL")
        or "https://api.wolai.com/v1/mcp",
    )
