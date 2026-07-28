<div align="center">

# 💧 Water Companion

**Your beautiful, animated desktop hydration reminder**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41cd52.svg)](https://pypi.org/project/PySide6/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/water-companion.svg)](https://pypi.org/project/water-companion/)

*A polished open-source desktop application that gently reminds you to drink water — with a cute animated mascot drawn entirely in code.*

</div>

---

## ✨ Features

- **🎨 Animated Water-Drop Mascot** — Drawn 100% with `QPainter`. No images, no assets. Blinking eyes, floating animation, smiling when you drink, sad when you skip.
- **🔔 Smart Reminders** — Configurable intervals from 5 minutes to 2 hours.
- **💫 Particle Effects** — Hearts & sparkles fly when you drink. Sad rain drops fall when you skip.
- **🖥️ System Tray** — Lives quietly in your tray. Pause, resume, or change interval without opening the window.
- **💻 Full CLI** — Control everything from your terminal with `water-companion` commands.
- **📁 Offline-First** — Settings stored locally in JSON. No cloud, no account, no internet.
- **🚀 PyPI-Ready** — Install with a single `pip install` command.
- **📦 Standalone Binary** — Build a `.exe` with PyInstaller.

---

## 🚀 Quick Start

### Install from PyPI

```bash
pip install water-companion
water-companion
```

That's it! The app launches, shows the setup window, and quietly moves to your system tray.

### Install for Development

```bash
git clone https://github.com/yourusername/water-companion
cd water-companion
pip install -e ".[dev]"
water-companion
```

---

## 💻 CLI Reference

```
water-companion                    Launch the app (default)
water-companion start              Launch the app
water-companion stop               Stop the running instance
water-companion pause              Pause reminders
water-companion resume             Resume paused reminders
water-companion status             Show current state and next reminder
water-companion config             Interactively change the interval
water-companion reset              Reset all settings to defaults
water-companion version            Print version
```

### Examples

```bash
# Check if it's running and when the next reminder fires
water-companion status

# Pause while you're in a meeting
water-companion pause

# Come back after the meeting
water-companion resume

# Change to every 15 minutes
water-companion config
```

---

## 🎮 How It Works

1. **Launch** — Run `water-companion` from terminal or double-click.
2. **Setup** — Choose your reminder interval (5 min to 2 hours).
3. **Click "Start"** — App minimises to system tray. Timer begins.
4. **Reminder fires** — Animated water drop slides in from the bottom-right corner.
5. **Respond:**
   - **Yes ✅** → Drop smiles → Hearts & sparkles fly → Timer restarts
   - **No ❌** → Drop looks sad → Sad drops fall → Timer restarts

---

## 🏗️ Architecture

```
water_companion/
├── main.py                   # App controller + IPC server
├── cli.py                    # Typer CLI
├── core/
│   ├── reminder_manager.py   # QTimer state machine (IDLE/RUNNING/PAUSED)
│   └── messages.py           # Encouragement + gentle reminder text
├── mascot/
│   ├── water_drop_widget.py  # QPainter mascot (no assets)
│   └── animations.py        # Slide, float, particle animations
├── ui/
│   ├── setup_window.py       # First-run setup window
│   ├── reminder_window.py    # Animated reminder popup
│   ├── tray_manager.py       # System tray icon + menu
│   └── styles.py             # QSS design system
├── settings/
│   └── config.py             # JSON config (load/save/reset)
└── utils/
    ├── constants.py          # App-wide constants
    └── logger.py             # Rotating file + console logger
```

**Design principles:**
- SOLID — each class has one responsibility
- Qt Signals/Slots — zero tight coupling between UI and logic
- No global state — everything passes through the controller
- Clean Architecture — UI, core, and data layers are fully independent

---

## 🧪 Running Tests

```bash
pip install pytest pytest-qt
pytest tests/ -v
```

Expected output:
```
tests/test_config.py            ✓  10 passed
tests/test_reminder_manager.py  ✓  12 passed
tests/test_messages.py          ✓   6 passed
```

---

## 📦 Building a Standalone Binary (Windows)

```bash
pip install pyinstaller
pyinstaller build.spec
```

The binary will be at `dist/water-companion/water-companion.exe`.

---

## 📤 Publishing to PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

---

## ⚙️ Configuration

Settings are stored at `~/.water-companion/config.json`:

```json
{
  "interval_minutes": 30,
  "reminders_enabled": true,
  "first_run": false
}
```

Logs are at `~/.water-companion/app.log` (rotating, max 6 MB).

---

## 🛠️ Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Language |
| PySide6 | 6.7+ | GUI framework |
| Typer | 0.12+ | CLI |
| Rich | 13.7+ | CLI formatting |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with tests
4. Run `pytest tests/ -v`
5. Submit a pull request

---

## 📄 License

[MIT](LICENSE) © Water Companion Contributors

---

<div align="center">
Made with 💧 and Python
</div>
