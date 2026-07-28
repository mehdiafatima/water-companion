"""
animations.py
=============
All QPropertyAnimation helpers and particle effects for Water Companion.

Particle classes are self-contained ephemeral widgets that appear, animate,
then delete themselves — no manual cleanup required by callers.
"""

from __future__ import annotations

import math
import random
from typing import Callable

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import QLabel, QWidget

from water_companion.utils.constants import (
    ANIM_FLOAT_MS,
    ANIM_PARTICLE_FADE_MS,
    ANIM_SLIDE_IN_MS,
    ANIM_SLIDE_OUT_MS,
    ANIM_HEART_COUNT,
    ANIM_SAD_PARTICLE_COUNT,
    FLOAT_AMPLITUDE_PX,
    TRAY_MARGIN_PX,
    REMINDER_WINDOW_HEIGHT,
    REMINDER_WINDOW_WIDTH,
)
from water_companion.utils.logger import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Slide Animations
# ─────────────────────────────────────────────────────────────────────────────

def make_slide_in_animation(widget: QWidget, screen_rect: QRect) -> QPropertyAnimation:
    """
    Build a slide-in animation that moves *widget* from below the screen
    to the bottom-right corner of *screen_rect*.

    Returns the animation (not started — caller starts it).
    """
    target_x = screen_rect.right() - REMINDER_WINDOW_WIDTH - TRAY_MARGIN_PX
    target_y = screen_rect.bottom() - REMINDER_WINDOW_HEIGHT - TRAY_MARGIN_PX

    start_pos = QPoint(target_x, screen_rect.bottom() + 10)
    end_pos = QPoint(target_x, target_y)

    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(ANIM_SLIDE_IN_MS)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    return anim


def make_slide_out_animation(widget: QWidget, screen_rect: QRect) -> QPropertyAnimation:
    """
    Build a slide-out animation that moves *widget* down and off screen.

    Returns the animation (not started — caller starts it).
    """
    current_pos = widget.pos()
    end_pos = QPoint(current_pos.x(), screen_rect.bottom() + REMINDER_WINDOW_HEIGHT + 20)

    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(ANIM_SLIDE_OUT_MS)
    anim.setStartValue(current_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.InCubic)
    return anim


# ─────────────────────────────────────────────────────────────────────────────
# Float Animation
# ─────────────────────────────────────────────────────────────────────────────

class FloatAnimator(QObject):
    """
    Continuously floats a widget up and down using a looping
    QSequentialAnimationGroup.
    """

    def __init__(self, widget: QWidget, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget = widget
        self._group: QSequentialAnimationGroup | None = None

    def start(self) -> None:
        """Begin the floating loop."""
        base_pos = self._widget.pos()

        up_pos = QPoint(base_pos.x(), base_pos.y() - FLOAT_AMPLITUDE_PX)
        down_pos = QPoint(base_pos.x(), base_pos.y() + FLOAT_AMPLITUDE_PX)

        up_anim = QPropertyAnimation(self._widget, b"pos")
        up_anim.setDuration(ANIM_FLOAT_MS // 2)
        up_anim.setStartValue(base_pos)
        up_anim.setEndValue(up_pos)
        up_anim.setEasingCurve(QEasingCurve.InOutSine)

        down_anim = QPropertyAnimation(self._widget, b"pos")
        down_anim.setDuration(ANIM_FLOAT_MS // 2)
        down_anim.setStartValue(up_pos)
        down_anim.setEndValue(down_pos)
        down_anim.setEasingCurve(QEasingCurve.InOutSine)

        self._group = QSequentialAnimationGroup(self._widget)
        self._group.addAnimation(up_anim)
        self._group.addAnimation(down_anim)
        self._group.setLoopCount(-1)   # infinite
        self._group.start()

    def stop(self) -> None:
        """Stop the float loop."""
        if self._group:
            self._group.stop()
            self._group = None


# ─────────────────────────────────────────────────────────────────────────────
# Particle: Heart
# ─────────────────────────────────────────────────────────────────────────────

class HeartParticle(QLabel):
    """
    A single floating heart emoji that rises and fades out automatically.
    Deletes itself when done.
    """

    def __init__(self, parent: QWidget, origin: QPoint) -> None:
        super().__init__("❤️", parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        font = QFont()
        font.setPointSize(random.randint(12, 20))
        self.setFont(font)
        self.adjustSize()

        # Random horizontal scatter
        x = origin.x() + random.randint(-50, 50)
        y = origin.y() + random.randint(-20, 20)
        self.move(x, y)
        self.show()

        # Rise animation
        end_y = y - random.randint(60, 120)
        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(ANIM_PARTICLE_FADE_MS)
        self._pos_anim.setStartValue(QPoint(x, y))
        self._pos_anim.setEndValue(QPoint(x, end_y))
        self._pos_anim.setEasingCurve(QEasingCurve.OutQuad)

        # Opacity / hide via timer (QLabel doesn't have windowOpacity property)
        QTimer.singleShot(ANIM_PARTICLE_FADE_MS, self.close)
        self._pos_anim.start()


class SparkleParticle(QLabel):
    """A sparkling star emoji that rises and fades."""

    CHARS = ["✨", "⭐", "💫", "🌟"]

    def __init__(self, parent: QWidget, origin: QPoint) -> None:
        super().__init__(random.choice(self.CHARS), parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        font = QFont()
        font.setPointSize(random.randint(10, 18))
        self.setFont(font)
        self.adjustSize()

        x = origin.x() + random.randint(-70, 70)
        y = origin.y() + random.randint(-30, 10)
        self.move(x, y)
        self.show()

        end_y = y - random.randint(50, 100)
        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(int(ANIM_PARTICLE_FADE_MS * 1.3))
        self._pos_anim.setStartValue(QPoint(x, y))
        self._pos_anim.setEndValue(QPoint(x + random.randint(-30, 30), end_y))
        self._pos_anim.setEasingCurve(QEasingCurve.OutQuart)

        QTimer.singleShot(int(ANIM_PARTICLE_FADE_MS * 1.3), self.close)
        self._pos_anim.start()


# ─────────────────────────────────────────────────────────────────────────────
# Particle: Sad
# ─────────────────────────────────────────────────────────────────────────────

class SadParticle(QLabel):
    """Small sad emoji that drifts downward and disappears."""

    CHARS = ["😢", "💧", "🌧️"]

    def __init__(self, parent: QWidget, origin: QPoint) -> None:
        super().__init__(random.choice(self.CHARS), parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        font = QFont()
        font.setPointSize(random.randint(10, 16))
        self.setFont(font)
        self.adjustSize()

        x = origin.x() + random.randint(-40, 40)
        y = origin.y() + random.randint(-10, 10)
        self.move(x, y)
        self.show()

        end_y = y + random.randint(40, 80)
        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(ANIM_PARTICLE_FADE_MS)
        self._pos_anim.setStartValue(QPoint(x, y))
        self._pos_anim.setEndValue(QPoint(x, end_y))
        self._pos_anim.setEasingCurve(QEasingCurve.InQuad)

        QTimer.singleShot(ANIM_PARTICLE_FADE_MS, self.close)
        self._pos_anim.start()


# ─────────────────────────────────────────────────────────────────────────────
# Particle launchers
# ─────────────────────────────────────────────────────────────────────────────

def spawn_happy_particles(parent: QWidget, origin: QPoint) -> None:
    """
    Launch a burst of hearts and sparkles around the given origin point.
    Each particle manages its own lifecycle.
    """
    for i in range(ANIM_HEART_COUNT):
        delay = i * 80
        QTimer.singleShot(delay, lambda o=origin: HeartParticle(parent, o))

    for i in range(ANIM_HEART_COUNT):
        delay = i * 100 + 40
        QTimer.singleShot(delay, lambda o=origin: SparkleParticle(parent, o))


def spawn_sad_particles(parent: QWidget, origin: QPoint) -> None:
    """
    Launch sad emoji particles around the given origin point.
    """
    for i in range(ANIM_SAD_PARTICLE_COUNT):
        delay = i * 100
        QTimer.singleShot(delay, lambda o=origin: SadParticle(parent, o))
