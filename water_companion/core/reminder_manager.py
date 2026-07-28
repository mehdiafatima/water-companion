"""
reminder_manager.py
====================
Business logic layer — owns the countdown timer and reminder state machine.

States
------
IDLE    → No timer running.
RUNNING → Countdown active.
PAUSED  → Countdown suspended by user.

Signals
-------
reminder_triggered  — Emitted when the countdown reaches zero.
state_changed(str)  — Emitted whenever the state changes.
"""

from __future__ import annotations

import logging
from enum import Enum, auto

from PySide6.QtCore import QObject, QTimer, Signal

from water_companion.utils.constants import DEFAULT_INTERVAL_MINUTES

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────

class ReminderState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()


# ─────────────────────────────────────────────────────────────────────────────
# Manager
# ─────────────────────────────────────────────────────────────────────────────

class ReminderManager(QObject):
    """
    Manages a single repeating countdown timer that emits ``reminder_triggered``
    when the configured interval elapses.

    All state transitions are logged and broadcast via ``state_changed``.
    """

    reminder_triggered = Signal()
    state_changed = Signal(str)

    def __init__(self, interval_minutes: int = DEFAULT_INTERVAL_MINUTES, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._interval_minutes: int = interval_minutes
        self._state: ReminderState = ReminderState.IDLE
        self._remaining_ms: int = 0   # used to resume from pause

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timer_fired)

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def state(self) -> ReminderState:
        return self._state

    @property
    def interval_minutes(self) -> int:
        return self._interval_minutes

    @property
    def remaining_seconds(self) -> int:
        """Approximate seconds remaining (0 when IDLE or PAUSED with no data)."""
        if self._state == ReminderState.RUNNING:
            return self._timer.remainingTime() // 1000
        if self._state == ReminderState.PAUSED:
            return self._remaining_ms // 1000
        return 0

    # ── Public interface ──────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the countdown from the full interval."""
        self._remaining_ms = self._interval_minutes * 60 * 1000
        self._timer.start(self._remaining_ms)
        self._set_state(ReminderState.RUNNING)
        log.info("Reminder timer started: %d minutes.", self._interval_minutes)

    def stop(self) -> None:
        """Stop and reset the timer."""
        self._timer.stop()
        self._remaining_ms = 0
        self._set_state(ReminderState.IDLE)
        log.info("Reminder timer stopped.")

    def pause(self) -> None:
        """Suspend the countdown, preserving remaining time."""
        if self._state != ReminderState.RUNNING:
            log.warning("pause() called but state is %s — ignored.", self._state)
            return
        self._remaining_ms = max(self._timer.remainingTime(), 0)
        self._timer.stop()
        self._set_state(ReminderState.PAUSED)
        log.info("Reminder timer paused. Remaining: %d ms.", self._remaining_ms)

    def resume(self) -> None:
        """Resume a paused countdown from where it left off."""
        if self._state != ReminderState.PAUSED:
            log.warning("resume() called but state is %s — ignored.", self._state)
            return
        self._timer.start(self._remaining_ms)
        self._set_state(ReminderState.RUNNING)
        log.info("Reminder timer resumed. Remaining: %d ms.", self._remaining_ms)

    def restart(self) -> None:
        """Restart the full countdown (called after user responds to reminder)."""
        self._timer.stop()
        self.start()
        log.info("Reminder timer restarted.")

    def set_interval(self, minutes: int) -> None:
        """
        Update the interval and immediately restart if currently running.

        Parameters
        ----------
        minutes : int
            New reminder interval in minutes (must be > 0).
        """
        if minutes <= 0:
            raise ValueError(f"Interval must be positive, got {minutes}.")
        self._interval_minutes = minutes
        log.info("Interval updated to %d minutes.", minutes)
        if self._state == ReminderState.RUNNING:
            self.start()   # restart with new interval

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_timer_fired(self) -> None:
        """Called by QTimer when the countdown reaches zero."""
        log.info("Reminder triggered!")
        self._set_state(ReminderState.IDLE)
        self.reminder_triggered.emit()

    def _set_state(self, new_state: ReminderState) -> None:
        self._state = new_state
        self.state_changed.emit(new_state.name)
