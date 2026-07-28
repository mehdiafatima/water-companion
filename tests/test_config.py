"""
test_config.py
==============
Unit tests for the settings/config module.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from water_companion.settings.config import AppConfig, load_config, save_config, reset_config
from water_companion.utils.constants import DEFAULT_INTERVAL_MINUTES


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _patch_config_file(tmp_path: Path):
    """Context manager that redirects CONFIG_FILE to a temp directory."""
    config_file = tmp_path / "config.json"
    return mock.patch("water_companion.settings.config.CONFIG_FILE", config_file)


# ─────────────────────────────────────────────────────────────────────────────
# AppConfig dataclass
# ─────────────────────────────────────────────────────────────────────────────

class TestAppConfig:
    def test_defaults(self):
        c = AppConfig()
        assert c.interval_minutes == DEFAULT_INTERVAL_MINUTES
        assert c.reminders_enabled is True
        assert c.first_run is True

    def test_to_dict_roundtrip(self):
        c = AppConfig(interval_minutes=15, reminders_enabled=False, first_run=False)
        d = c.to_dict()
        c2 = AppConfig.from_dict(d)
        assert c == c2

    def test_from_dict_ignores_unknown_keys(self):
        d = {"interval_minutes": 10, "unknown_key": "value", "reminders_enabled": True, "first_run": False}
        c = AppConfig.from_dict(d)
        assert c.interval_minutes == 10
        assert not hasattr(c, "unknown_key")


# ─────────────────────────────────────────────────────────────────────────────
# load_config
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadConfig:
    def test_returns_defaults_when_no_file(self, tmp_path):
        with _patch_config_file(tmp_path):
            config = load_config()
        assert config.interval_minutes == DEFAULT_INTERVAL_MINUTES
        assert config.first_run is True

    def test_loads_valid_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        data = {"interval_minutes": 45, "reminders_enabled": False, "first_run": False}
        config_file.write_text(json.dumps(data))

        with mock.patch("water_companion.settings.config.CONFIG_FILE", config_file):
            config = load_config()

        assert config.interval_minutes == 45
        assert config.reminders_enabled is False
        assert config.first_run is False

    def test_returns_defaults_on_corrupt_json(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("{not valid json}")

        with mock.patch("water_companion.settings.config.CONFIG_FILE", config_file):
            config = load_config()

        assert config.interval_minutes == DEFAULT_INTERVAL_MINUTES


# ─────────────────────────────────────────────────────────────────────────────
# save_config
# ─────────────────────────────────────────────────────────────────────────────

class TestSaveConfig:
    def test_saves_and_reloads(self, tmp_path):
        config_file = tmp_path / "config.json"
        original = AppConfig(interval_minutes=60, reminders_enabled=True, first_run=False)

        with mock.patch("water_companion.settings.config.CONFIG_FILE", config_file):
            save_config(original)
            loaded = load_config()

        assert loaded.interval_minutes == 60
        assert loaded.first_run is False

    def test_creates_parent_dirs(self, tmp_path):
        config_file = tmp_path / "deep" / "nested" / "config.json"
        with mock.patch("water_companion.settings.config.CONFIG_FILE", config_file):
            save_config(AppConfig())
        assert config_file.exists()


# ─────────────────────────────────────────────────────────────────────────────
# reset_config
# ─────────────────────────────────────────────────────────────────────────────

class TestResetConfig:
    def test_deletes_file_and_returns_defaults(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"interval_minutes": 60, "reminders_enabled": False, "first_run": False}))

        with mock.patch("water_companion.settings.config.CONFIG_FILE", config_file):
            result = reset_config()

        assert not config_file.exists()
        assert result.interval_minutes == DEFAULT_INTERVAL_MINUTES
        assert result.first_run is True

    def test_no_error_when_no_file(self, tmp_path):
        with _patch_config_file(tmp_path):
            result = reset_config()  # should not raise
        assert isinstance(result, AppConfig)
