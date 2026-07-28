"""
messages.py
===========
Curated sets of encouraging and gentle reminder messages.

Both functions are pure — no side effects — making them trivially testable.
"""

import random

# ─────────────────────────────────────────────────────────────────────────────
# Positive reinforcement messages  (shown on "Yes" response)
# ─────────────────────────────────────────────────────────────────────────────

_ENCOURAGEMENT_MESSAGES: list[str] = [
    "Amazing! Keep it up! 💧",
    "You're doing great! Your body thanks you! 🌊",
    "Hydration hero! 🏆",
    "Every sip counts! You're on a roll! ✨",
    "That's the spirit! Stay refreshed! 💙",
    "Wonderful! Hydration = Superpower! ⚡",
    "You just levelled up your health! 🎉",
    "Body: 'Thank you!' Brain: 'More please!' 🧠💧",
    "Sip sip hooray! Keep going! 🎊",
    "Your cells are dancing with joy right now! 💃",
    "Science says you just boosted your focus! 🔬✨",
    "Another great choice! You're unstoppable! 🚀",
    "Well done! A hydrated you is a happy you! 😊",
    "That's what I'm talking about! Stay hydrated! 🌟",
    "Your future self is grateful right now! 🙌",
]

# ─────────────────────────────────────────────────────────────────────────────
# Gentle nudge messages  (shown on "No" response)
# ─────────────────────────────────────────────────────────────────────────────

_GENTLE_REMINDERS: list[str] = [
    "No worries! Remember to hydrate soon. 💧",
    "That's okay! Even small sips help. Try soon! 🌊",
    "Totally fine! I'll check in on you again. 😊",
    "No rush! Just a friendly nudge for next time. 💙",
    "It's all good! Try to grab some water soon. ✨",
    "I'll remind you again! Take care of yourself. 🤗",
    "Everyone forgets sometimes! I've got your back. 💪",
    "No stress! Even a few sips make a difference. 🌟",
    "Your body believes in you! Try to drink soon. 😄",
    "Small steps count! I'll check in again shortly. 🌈",
]

# ─────────────────────────────────────────────────────────────────────────────
# Subtitle messages shown in the reminder popup
# ─────────────────────────────────────────────────────────────────────────────

_REMINDER_SUBTITLES: list[str] = [
    "Have you drunk water?",
    "Time for a quick sip! 💧",
    "Your body is 60% water — top it up!",
    "A moment for hydration!",
    "Don't forget to sip! 🌊",
    "Water break time!",
]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_encouragement_message() -> str:
    """Return a random positive encouragement message for the 'Yes' response."""
    return random.choice(_ENCOURAGEMENT_MESSAGES)


def get_gentle_reminder() -> str:
    """Return a random gentle nudge for the 'No' response."""
    return random.choice(_GENTLE_REMINDERS)


def get_reminder_subtitle() -> str:
    """Return a random subtitle for the reminder popup."""
    return random.choice(_REMINDER_SUBTITLES)
