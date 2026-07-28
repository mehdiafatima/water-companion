"""
constants.py
============
Application-wide constants for Water Companion.
All magic strings and values live here — never scattered across modules.
"""

import sys
from pathlib import Path

# ──────────────────────────────────────────────
# Identity
# ──────────────────────────────────────────────
APP_NAME: str = "Water Companion"
APP_ID: str = "water-companion"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Water Companion Contributors"
APP_URL: str = "https://github.com/yourusername/water-companion"

# ──────────────────────────────────────────────
# File-system paths
# ──────────────────────────────────────────────
APP_DATA_DIR: Path = Path.home() / ".water-companion"
CONFIG_FILE: Path = APP_DATA_DIR / "config.json"
LOG_FILE: Path = APP_DATA_DIR / "app.log"
PID_FILE: Path = APP_DATA_DIR / "app.pid"
SOCKET_FILE: Path = APP_DATA_DIR / "app.sock"  # Unix IPC socket
IPC_PORT: int = 47832  # TCP port for IPC on Windows

# ──────────────────────────────────────────────
# Reminder intervals  (label → minutes)
# ──────────────────────────────────────────────
INTERVAL_OPTIONS: dict[str, int] = {
    "5 Minutes": 5,
    "10 Minutes": 10,
    "15 Minutes": 15,
    "30 Minutes": 30,
    "45 Minutes": 45,
    "1 Hour": 60,
    "2 Hours": 120,
}

DEFAULT_INTERVAL_LABEL: str = "30 Minutes"
DEFAULT_INTERVAL_MINUTES: int = INTERVAL_OPTIONS[DEFAULT_INTERVAL_LABEL]

# ──────────────────────────────────────────────
# Animation timing (milliseconds)
# ──────────────────────────────────────────────
ANIM_SLIDE_IN_MS: int = 600
ANIM_SLIDE_OUT_MS: int = 500
ANIM_FLOAT_MS: int = 2000
ANIM_BLINK_INTERVAL_MS: int = 3500
ANIM_PARTICLE_FADE_MS: int = 1200
ANIM_HEART_COUNT: int = 6
ANIM_SAD_PARTICLE_COUNT: int = 5

# ──────────────────────────────────────────────
# Mascot / reminder window geometry
# ──────────────────────────────────────────────
REMINDER_WINDOW_WIDTH: int = 320
REMINDER_WINDOW_HEIGHT: int = 380
MASCOT_SIZE: int = 140           # px — water drop bounding box
FLOAT_AMPLITUDE_PX: int = 8     # how many pixels the mascot floats up/down
TRAY_MARGIN_PX: int = 20        # gap from screen edge

# ──────────────────────────────────────────────
# Platform helpers
# ──────────────────────────────────────────────
IS_WINDOWS: bool = sys.platform == "win32"
IS_MACOS: bool = sys.platform == "darwin"
IS_LINUX: bool = sys.platform.startswith("linux")
