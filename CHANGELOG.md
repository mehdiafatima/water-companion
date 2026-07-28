# Changelog

All notable changes to Water Companion are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2024-07-28

### Added
- First public release 🎉
- Beautiful QPainter water-drop mascot with blink, float, smile, and sad states
- Smooth slide-in / slide-out animations via `QPropertyAnimation`
- Happy particles (hearts + sparkles) and sad particles on responses
- Configurable reminder intervals: 5m, 10m, 15m, 30m, 45m, 1h, 2h
- System tray with Pause / Resume / Change Interval / Quit
- JSON config persisted at `~/.water-companion/config.json`
- Typer CLI: `start`, `stop`, `pause`, `resume`, `status`, `config`, `reset`, `version`
- TCP IPC server for CLI ↔ GUI communication
- Rotating file logger at `~/.water-companion/app.log`
- PyPI-ready packaging via `pyproject.toml` + Hatchling
- PyInstaller spec for standalone Windows binary
- Full pytest test suite (config, state machine, messages)
- MIT License
