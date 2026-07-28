"""
core/__init__.py
"""
from water_companion.core.reminder_manager import ReminderManager, ReminderState
from water_companion.core.messages import (
    get_encouragement_message,
    get_gentle_reminder,
    get_reminder_subtitle,
)

__all__ = [
    "ReminderManager",
    "ReminderState",
    "get_encouragement_message",
    "get_gentle_reminder",
    "get_reminder_subtitle",
]
