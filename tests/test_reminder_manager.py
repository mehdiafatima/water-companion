"""
test_reminder_manager.py
========================
Unit tests for the core/reminder_manager module.

Note: ReminderManager is a QObject so we need a QApplication instance.
We use pytest-qt or a manual QApplication fixture.
"""

import pytest
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# QApplication fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def qapp():
    """Provide a QApplication for Qt-based tests."""
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestReminderManager:
    """Tests for ReminderManager state transitions."""

    def _make_manager(self, qapp, minutes: int = 30):
        from water_companion.core.reminder_manager import ReminderManager
        return ReminderManager(interval_minutes=minutes)

    def test_initial_state_is_idle(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        assert mgr.state == ReminderState.IDLE

    def test_start_sets_running(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        mgr.start()
        assert mgr.state == ReminderState.RUNNING
        mgr.stop()

    def test_stop_sets_idle(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        mgr.start()
        mgr.stop()
        assert mgr.state == ReminderState.IDLE

    def test_pause_sets_paused(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        mgr.start()
        mgr.pause()
        assert mgr.state == ReminderState.PAUSED
        mgr.stop()

    def test_resume_from_paused_sets_running(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        mgr.start()
        mgr.pause()
        mgr.resume()
        assert mgr.state == ReminderState.RUNNING
        mgr.stop()

    def test_pause_ignored_when_not_running(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        # Should not raise — logged warning only
        mgr.pause()
        assert mgr.state == ReminderState.IDLE

    def test_resume_ignored_when_not_paused(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)
        mgr.resume()
        assert mgr.state == ReminderState.IDLE

    def test_set_interval_updates_value(self, qapp):
        mgr = self._make_manager(qapp)
        mgr.set_interval(15)
        assert mgr.interval_minutes == 15

    def test_set_interval_raises_on_zero(self, qapp):
        mgr = self._make_manager(qapp)
        with pytest.raises(ValueError):
            mgr.set_interval(0)

    def test_set_interval_raises_on_negative(self, qapp):
        mgr = self._make_manager(qapp)
        with pytest.raises(ValueError):
            mgr.set_interval(-5)

    def test_state_changed_signal_emitted(self, qapp):
        from water_companion.core.reminder_manager import ReminderState
        mgr = self._make_manager(qapp)

        received: list[str] = []
        mgr.state_changed.connect(lambda s: received.append(s))

        mgr.start()
        mgr.pause()
        mgr.resume()
        mgr.stop()

        assert "RUNNING" in received
        assert "PAUSED" in received
        assert "IDLE" in received

    def test_remaining_seconds_zero_when_idle(self, qapp):
        mgr = self._make_manager(qapp)
        assert mgr.remaining_seconds == 0

    def test_remaining_seconds_nonzero_when_running(self, qapp):
        mgr = self._make_manager(qapp, minutes=10)
        mgr.start()
        # Should be close to 10 * 60 seconds
        assert mgr.remaining_seconds > 0
        mgr.stop()
