"""Repository-local paths and non-secret service settings."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from agent.env_utils import get_env

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_DATABASE_URL = get_env("AGENT_DATABASE_URL", get_env("DATABASE_URL"))
DATA_DIR = Path(get_env("AI_CODING_DATA_DIR", str(PROJECT_ROOT / "data"))).resolve()
LOG_DIR = Path(get_env("AI_CODING_LOG_DIR", str(PROJECT_ROOT / "logs"))).resolve()
SKILLS_DIR = PROJECT_ROOT / "agent" / "skills"
LOG_LEVEL = get_env("AI_CODING_LOG_LEVEL", "INFO").upper()
LOG_ROTATION_WHEN = get_env("AI_CODING_LOG_WHEN", "midnight")
LOG_ROTATION_INTERVAL = int(get_env("AI_CODING_LOG_INTERVAL", "1"))
LOG_RETENTION_DAYS = int(get_env("AI_CODING_LOG_RETENTION_DAYS", "14"))


def backend_log_path(target_date: date | None = None) -> Path:
    return LOG_DIR / ("backend.log" if target_date is None else f"backend.log.{target_date.isoformat()}")


def agent_log_path(target_date: date | None = None) -> Path:
    return LOG_DIR / ("agent-runs.log" if target_date is None else f"agent-runs.log.{target_date.isoformat()}")
