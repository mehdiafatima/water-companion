"""
test_messages.py
================
Unit tests for the core/messages module.
All functions are pure — no setup needed.
"""

import pytest
from water_companion.core.messages import (
    get_encouragement_message,
    get_gentle_reminder,
    get_reminder_subtitle,
)


class TestMessages:
    def test_encouragement_returns_string(self):
        msg = get_encouragement_message()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_gentle_reminder_returns_string(self):
        msg = get_gentle_reminder()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_subtitle_returns_string(self):
        msg = get_reminder_subtitle()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_encouragement_varies(self):
        """The function should not always return the same string."""
        results = {get_encouragement_message() for _ in range(50)}
        assert len(results) > 1

    def test_gentle_reminder_varies(self):
        results = {get_gentle_reminder() for _ in range(50)}
        assert len(results) > 1

    def test_subtitle_varies(self):
        results = {get_reminder_subtitle() for _ in range(50)}
        assert len(results) > 1
