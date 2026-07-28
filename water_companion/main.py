"""
main.py
=======
Application entry point and orchestrator for Water Companion.

This module wires together:
  - Settings (AppConfig)
  - ReminderManager (timer + state machine)
  - SetupWindow (first-run / settings)
  - ReminderWindow (animated popup)
  - TrayManager (system tray)
  - IPC server (TCP socket for CLI control)
  - SIGINT (Ctrl+C) handling — reopens the setup window to pick a new
    interval instead of killing the whole application.

All inter-component communication goes through Qt signals.
No tight coupling between UI and core logic.
"""

from __future__ import annotations

import json
import signal
import sys
import threading
import logging

from PySide6.QtCore import Qt, QMetaObject, Q_ARG, QTimer
from PySide6.QtWidgets import QApplication

from water_companion.core.reminder_manager import ReminderManager, ReminderState
from water_companion.settings.config import AppConfig, load_config, save_config
from water_companion.ui.reminder_window import ReminderWindow
from water_companion.ui.setup_window import SetupWindow
from water_companion.ui.tray_manager import TrayManager
from water_companion.utils.constants import APP_NAME, APP_VERSION, IPC_PORT
from water_companion.utils.logger import get_logger, setup_logging

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# IPC Server (runs on a background thread)
# ─────────────────────────────────────────────────────────────────────────────

class IpcServer(threading.Thread):
    """
    Minimal TCP server that listens on localhost:IPC_PORT for CLI commands.

    Supported commands (newline-terminated):
      ping           → responds "OK"
      open           → triggers open_requested callback
      pause          → triggers pause_requested callback
      resume         → triggers resume_requested callback
      quit           → triggers quit_requested callback
      interval:<N>   → triggers interval_changed callback with N minutes
      status         → responds with JSON status payload
    """

    def __init__(self, controller: "WaterCompanionApp") -> None:
        super().__init__(daemon=True, name="ipc-server")
        self._controller = controller
        self._running = True

    def run(self) -> None:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("127.0.0.1", IPC_PORT))
                server.listen(4)
                server.settimeout(1.0)
                log.info("IPC server listening on port %d.", IPC_PORT)

                while self._running:
                    try:
                        conn, _ = server.accept()
                        threading.Thread(
                            target=self._handle,
                            args=(conn,),
                            daemon=True,
                        ).start()
                    except TimeoutError:
                        continue
        except OSError as exc:
            log.warning("IPC server could not start: %s", exc)

    def stop(self) -> None:
        self._running = False

    def _handle(self, conn) -> None:
        """Handle a single client connection."""
        try:
            with conn:
                raw = conn.recv(256).decode().strip()
                response = self._dispatch(raw)
                conn.sendall((response + "\n").encode())
        except OSError:
            pass

    def _dispatch(self, command: str) -> str:
        """
        Dispatch a CLI command.  All Qt calls are marshalled to the main thread
        via Qt.QueuedConnection.
        """
        c = self._controller

        if command == "ping":
            return "OK"
        elif command == "open":
            QMetaObject.invokeMethod(c._setup_window, "show_window", Qt.QueuedConnection)
            return "OK"
        elif command == "pause":
            QMetaObject.invokeMethod(c._reminder_manager, "pause", Qt.QueuedConnection)
            return "OK"
        elif command == "resume":
            QMetaObject.invokeMethod(c._reminder_manager, "resume", Qt.QueuedConnection)
            return "OK"
        elif command == "quit":
            QMetaObject.invokeMethod(c._app, "quit", Qt.QueuedConnection)
            return "OK"
        elif command.startswith("interval:"):
            try:
                minutes = int(command.split(":")[1])
                # Schedule on main thread
                QMetaObject.invokeMethod(
                    c._reminder_manager,
                    "set_interval",
                    Qt.QueuedConnection,
                    Q_ARG(int, minutes),
                )
                return "OK"
            except (IndexError, ValueError):
                return "ERROR"
        elif command == "status":
            state = c._reminder_manager.state
            payload = {
                "state": state.name,
                "interval_minutes": c._reminder_manager.interval_minutes,
                "remaining_seconds": c._reminder_manager.remaining_seconds,
            }
            return json.dumps(payload)
        else:
            return "UNKNOWN"


# ─────────────────────────────────────────────────────────────────────────────
# Application Controller
# ─────────────────────────────────────────────────────────────────────────────

class WaterCompanionApp:
    """
    Top-level controller that owns all components and connects their signals.

    Responsibilities
    ----------------
    - Bootstrap the QApplication.
    - Load / save configuration.
    - Coordinate the reminder timer, setup window, reminder popup, and tray.
    - Run the IPC server for CLI control.
    - Handle Ctrl+C (SIGINT) from the terminal: instead of terminating the
      whole app, it pauses the current reminder timer and reopens the
      SetupWindow so the user can pick a brand-new interval.
    """

    def __init__(self) -> None:
        # Qt application must exist before any QWidget
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setApplicationName(APP_NAME)
        self._app.setApplicationVersion(APP_VERSION)
        # Keep running even if all windows are closed (lives in tray)
        self._app.setQuitOnLastWindowClosed(False)

        setup_logging()
        log.info("=== %s v%s starting ===", APP_NAME, APP_VERSION)

        # Load config
        self._config: AppConfig = load_config()

        # Core
        self._reminder_manager = ReminderManager(self._config.interval_minutes)

        # UI components
        self._setup_window = SetupWindow(self._config)
        self._reminder_window = ReminderWindow()
        self._tray = TrayManager()

        # IPC
        self._ipc_server = IpcServer(self)

        self._wire_signals()
        self._setup_sigint_handler()

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _wire_signals(self) -> None:
        """Connect all inter-component signals."""

        # Setup window → reminder manager
        self._setup_window.start_requested.connect(self._on_start_requested)

        # Reminder manager → reminder window
        self._reminder_manager.reminder_triggered.connect(self._on_reminder_triggered)
        self._reminder_manager.state_changed.connect(self._on_state_changed)

        # Reminder window → timer restart
        self._reminder_window.responded.connect(self._on_reminder_responded)

        # Tray → various handlers
        self._tray.open_requested.connect(self._on_open_requested)
        self._tray.pause_requested.connect(self._on_pause_requested)
        self._tray.resume_requested.connect(self._on_resume_requested)
        self._tray.interval_changed.connect(self._on_interval_changed)
        self._tray.quit_requested.connect(self._on_quit_requested)

    def _setup_sigint_handler(self) -> None:
        """
        Wire up Ctrl+C (SIGINT) handling.

        Qt's event loop is native C++ code, so a plain `signal.signal()`
        handler will not fire until control returns to the Python
        interpreter. The classic fix is to run a small, harmless QTimer
        that periodically "wakes up" the interpreter so pending Python
        signal handlers actually get a chance to execute.
        """
        signal.signal(signal.SIGINT, self._handle_sigint)

        # Lets the Python interpreter regain control periodically so the
        # SIGINT handler above can actually run while the Qt loop is active.
        self._sigint_pump = QTimer()
        self._sigint_pump.timeout.connect(lambda: None)
        self._sigint_pump.start(200)  # ms

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    def run(self) -> int:
        """
        Start the application.

        Returns
        -------
        int
            Exit code from QApplication.exec().
        """
        # Start IPC server in background thread
        self._ipc_server.start()

        # Show tray icon
        self._tray.show()

        # Always ask for the interval on startup — whether this is the very
        # first run or a later one. The reminder timer only starts once the
        # user confirms an interval via the setup window (see
        # _on_start_requested), so nothing runs silently in the background
        # with a stale, previously-saved value.
        log.info(
            "Startup: asking user for interval (last saved: %d min).",
            self._config.interval_minutes,
        )
        self._setup_window.show_window()
        self._setup_window.raise_()
        self._setup_window.activateWindow()

        return self._app.exec()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_start_requested(self, minutes: int) -> None:
        """User picked a new interval and clicked 'Start Reminder'."""
        self._config.interval_minutes = minutes
        save_config(self._config)

        # Make sure any previously running timer is fully stopped before
        # starting a fresh one — avoids the "old interval still ticking
        # in the background" bug.
        self._reminder_manager.stop()
        self._reminder_manager.set_interval(minutes)
        self._reminder_manager.start()

        self._tray.show_message(APP_NAME, f"💧 Reminders active every {minutes} min!")
        log.info("Reminders started with interval: %d min.", minutes)

    def _on_reminder_triggered(self) -> None:
        """Timer fired — show the animated reminder popup."""
        self._reminder_window.show_reminder()

    def _on_reminder_responded(self, drank: bool) -> None:
        """User responded to reminder — restart the timer."""
        self._reminder_manager.restart()
        if drank:
            log.info("User drank water. Timer restarted.")
        else:
            log.info("User skipped water. Timer restarted.")

    def _on_state_changed(self, state_name: str) -> None:
        """Keep the tray icon in sync with timer state."""
        self._tray.set_paused(state_name == ReminderState.PAUSED.name)

    def _on_open_requested(self) -> None:
        """Tray 'Open' — show setup/settings window."""
        self._setup_window.show_window()

    def _on_pause_requested(self) -> None:
        self._reminder_manager.pause()
        self._tray.show_message(APP_NAME, "⏸ Reminders paused.")
        log.info("Reminders paused via tray.")

    def _on_resume_requested(self) -> None:
        self._reminder_manager.resume()
        self._tray.show_message(APP_NAME, "▶ Reminders resumed.")
        log.info("Reminders resumed via tray.")

    def _on_interval_changed(self, minutes: int) -> None:
        """User picked a new interval from tray submenu."""
        self._config.interval_minutes = minutes
        save_config(self._config)
        self._reminder_manager.set_interval(minutes)
        self._setup_window.update_interval_display(minutes)
        self._tray.show_message(APP_NAME, f"⏱ Interval updated to {minutes} min.")
        log.info("Interval changed to %d min via tray.", minutes)

    def _on_quit_requested(self) -> None:
        log.info("Quit requested via tray.")
        self._ipc_server.stop()
        self._reminder_manager.stop()
        self._tray.hide()
        self._app.quit()

    def _handle_sigint(self, signum, frame) -> None:
        """
        Called when the user presses Ctrl+C in the terminal.

        Instead of terminating the app, we:
          1. Fully stop the currently running reminder timer (so the old
             interval can't keep ticking in the background).
          2. Reopen the SetupWindow, front-and-center, so the user can pick
             a brand-new interval and press Start again.

        The app keeps living in the tray/IPC server exactly as before —
        the ONLY way to actually exit is via the tray's "Quit" option
        (or an IPC "quit" command).
        """
        # Print directly to the console (not just the logger) so you get
        # instant, unmistakable confirmation that the handler actually fired.
        print("\n[Water Companion] Ctrl+C detected — reopening setup window...", flush=True)
        log.info("Ctrl+C received — stopping current timer and reopening setup window.")

        # Stop (not just pause) so no stale timer keeps running underneath.
        self._reminder_manager.stop()

        # In case a reminder popup happens to be showing, hide it.
        self._reminder_window.hide()

        # Bring the setup window back to pick a fresh interval.
        self._setup_window.show_window()
        self._setup_window.raise_()
        self._setup_window.activateWindow()


# ─────────────────────────────────────────────────────────────────────────────
# Script entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_app() -> None:
    """Entry point called by the CLI and by PyInstaller."""
    controller = WaterCompanionApp()
    sys.exit(controller.run())


if __name__ == "__main__":
    run_app()
