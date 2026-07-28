<div align="center">

# 💧 Water Companion


A beautiful, animated desktop hydration reminder built with **Python** and **PySide6**.

Water Companion helps you build a healthier habit by gently reminding you to drink water while you work, study, code, or game. It features a fully animated water-drop mascot drawn entirely in code using **QPainter**, with no external image assets.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41cd52.svg)](https://pypi.org/project/PySide6/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/water-companion.svg)](https://pypi.org/project/water-companion/)

*A polished open-source desktop application that gently reminds you to drink water — with a cute animated mascot drawn entirely in code.*

</div>


## ✨ Features

- 💧 Animated water-drop mascot drawn entirely with **QPainter**
- 😊 Blinking eyes with happy and sad expressions
- ✨ Floating animations, hearts, sparkles, and rain effects
- 🔔 Custom reminder intervals from **5 minutes to 2 hours**
- 🖥️ Runs quietly in the **System Tray**
- 💻 Built-in **Command Line Interface (CLI)**
- 📁 Offline-first with local JSON configuration
- 🚀 Available on **PyPI**
- 🎨 Clean and modern desktop interface

---

# 🚀 Installation

## Prerequisites

Install **Python 3.12 or later** from:

https://www.python.org/downloads/

> **Important:** During installation, make sure **"Add Python to PATH"** is checked.

Verify the installation:

```bash
python --version
```

Upgrade pip (recommended):

```bash
python -m pip install --upgrade pip
```

---

## Install Water Companion

```bash
pip install water-companion
```

Launch the application:

```bash
water-companion
```

That's it! 🎉

On the first launch, choose your preferred reminder interval and click **Start**. The application will automatically minimize to the system tray and begin sending hydration reminders.

---

# 💻 CLI Commands

| Command | Description |
|---------|-------------|
| `water-companion` | Launch the application |
| `water-companion start` | Start Water Companion |
| `water-companion stop` | Stop the running instance |
| `water-companion pause` | Pause reminders |
| `water-companion resume` | Resume reminders |
| `water-companion status` | Display the current status |
| `water-companion config` | Change the reminder interval |
| `water-companion reset` | Restore default settings |
| `water-companion version` | Display the installed version |

---

## Example

Check the current reminder status:

```bash
water-companion status
```

Pause reminders:

```bash
water-companion pause
```

Resume reminders:

```bash
water-companion resume
```

Change the reminder interval:

```bash
water-companion config
```

---

# 🎮 How It Works

1. Launch the application.
2. Select a reminder interval between **5 minutes** and **2 hours**.
3. Click **Start**.
4. The application moves to the system tray and starts the timer.
5. When it's time to drink water, an animated reminder appears.
6. Respond to the reminder:
   - ✅ **Yes** — The mascot smiles, heart and sparkle animations play, and the timer restarts.
   - ❌ **No** — The mascot becomes sad, rain animations appear, and the timer restarts.

---

# 🏗️ Project Structure

```
water_companion/
├── main.py
├── cli.py
├── core/
│   ├── reminder_manager.py
│   └── messages.py
├── mascot/
│   ├── water_drop_widget.py
│   └── animations.py
├── ui/
│   ├── setup_window.py
│   ├── reminder_window.py
│   ├── tray_manager.py
│   └── styles.py
├── settings/
│   └── config.py
└── utils/
    ├── constants.py
    └── logger.py
```

---

# 🧠 Architecture

The project follows modern software engineering principles:

- SOLID Principles
- Clean Architecture
- Qt Signals & Slots
- Modular Components
- Separation of Concerns
- Offline-first Design

---

# 🧪 Running Tests

Install testing dependencies:

```bash
pip install pytest pytest-qt
```

Run the test suite:

```bash
pytest tests/ -v
```

---

# 📦 Building the Package

```bash
pip install build
python -m build
```

The generated distributions will be available inside the **dist/** directory.

---

# 📤 Publishing to PyPI

```bash
pip install twine
twine upload dist/*
```

---

# ⚙️ Configuration

Application settings are stored locally:

```
~/.water-companion/config.json
```

Example:

```json
{
  "interval_minutes": 30,
  "reminders_enabled": true,
  "first_run": false
}
```

Application logs are stored in:

```
~/.water-companion/app.log
```

---

# 🛠️ Requirements

| Dependency | Version |
|------------|---------|
| Python | 3.12+ |
| PySide6 | 6.7+ |
| Typer | 0.12+ |
| Rich | 13.7+ |

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push your branch

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the **MIT License**.

---

## ❤️ Support

If you find this project useful, consider giving it a ⭐ on GitHub and sharing it with others.

Stay hydrated. 💧