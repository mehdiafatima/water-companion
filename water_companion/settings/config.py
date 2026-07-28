"""
config.py
=========
Handles loading and persisting application settings via JSON.

Schema
------
{
    "interval_minutes": 30,
    "reminders_enabled": true,
    "first_run": true
}
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from water_companion.utils.constants import (
    CONFIG_FILE,
    DEFAULT_INTERVAL_MINUTES,
)

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AppConfig:
    """All persisted user preferences for Water Companion."""

    interval_minutes: int = DEFAULT_INTERVAL_MINUTES
    reminders_enabled: bool = True
    first_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dict for JSON serialisation."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AppConfig":
        """Create an AppConfig from a dict, ignoring unknown keys safely."""
        valid_keys = AppConfig.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return AppConfig(**filtered)


# ─────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_config_dir() -> None:
    """Create the config directory if it does not exist."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> AppConfig:
    """
    Load configuration from disk.

    Returns the stored config on success, or a fresh default AppConfig if
    the file does not exist or is corrupt.
    """
    _ensure_config_dir()

    if not CONFIG_FILE.exists():
        log.info("No config file found — using defaults.")
        return AppConfig()

    try:
        raw: dict[str, Any] = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        config = AppConfig.from_dict(raw)
        log.info("Config loaded: interval=%d min, enabled=%s", config.interval_minutes, config.reminders_enabled)
        return config
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        log.warning("Config file corrupt (%s) — resetting to defaults.", exc)
        return AppConfig()


def save_config(config: AppConfig) -> None:
    """
    Persist the given AppConfig to disk as JSON.

    Raises
    ------
    OSError
        If the file cannot be written (e.g. permissions error).
    """
    _ensure_config_dir()
    data = json.dumps(config.to_dict(), indent=2)
    CONFIG_FILE.write_text(data, encoding="utf-8")
    log.info("Config saved: %s", config.to_dict())


def reset_config() -> AppConfig:
    """Delete the config file and return a fresh default config."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        log.info("Config file deleted — reset to defaults.")
    return AppConfig()
