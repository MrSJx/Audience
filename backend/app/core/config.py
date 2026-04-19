import os
from dataclasses import dataclass
from pathlib import Path


def _bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "Audience API"
    app_version: str = "0.3.0"
    project_root: Path = Path(__file__).resolve().parents[2]
    uploads_dir: Path = project_root / "uploads"
    data_dir: Path = project_root / "data"
    database_path: Path = data_dir / "audience.db"
    ollama_base_url: str = os.getenv("AUDIENCE_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("AUDIENCE_OLLAMA_MODEL", "llama3.2")
    ollama_timeout_seconds: float = _float_env("AUDIENCE_OLLAMA_TIMEOUT_SECONDS", 60.0)
    ollama_healthcheck_seconds: float = _float_env("AUDIENCE_OLLAMA_HEALTHCHECK_SECONDS", 0.35)
    use_heuristic_fallback: bool = _bool_env("AUDIENCE_USE_HEURISTIC_FALLBACK", False)


settings = Settings()
