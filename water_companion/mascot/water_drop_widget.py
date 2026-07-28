"""
water_drop_widget.py
====================
Animated water-drop mascot drawn entirely with QPainter.

No external images, no assets — 100% code.

The mascot supports three emotional states:
- NORMAL  → Neutral expression, gentle blink
- HAPPY   → Wide smile, rosy cheeks
- SAD     → Downturned mouth, teary eyes
"""

from __future__ import annotations

import math
from enum import Enum, auto

from PySide6.QtCore import (
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from water_companion.utils.constants import (
    ANIM_BLINK_INTERVAL_MS,
    MASCOT_SIZE,
)
from water_companion.utils.logger import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Emotion state
# ─────────────────────────────────────────────────────────────────────────────

class MascotState(Enum):
    NORMAL = auto()
    HAPPY = auto()
    SAD = auto()


# ─────────────────────────────────────────────────────────────────────────────
# Water Drop Widget
# ─────────────────────────────────────────────────────────────────────────────

class WaterDropWidget(QWidget):
    """
    A transparent widget that renders the Water Companion mascot via QPainter.

    Signals
    -------
    blink_done : emitted after each blink cycle (informational)
    """

    blink_done = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(QSize(MASCOT_SIZE, MASCOT_SIZE))

        self._state: MascotState = MascotState.NORMAL
        self._is_blinking: bool = False
        self._blink_frame: int = 0   # 0 = open, 1 = half, 2 = closed, 3 = half

        # Blink scheduler
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._start_blink)
        self._blink_timer.start(ANIM_BLINK_INTERVAL_MS)

        self._blink_anim_timer = QTimer(self)
        self._blink_anim_timer.setInterval(60)
        self._blink_anim_timer.timeout.connect(self._advance_blink)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_state(self, state: MascotState) -> None:
        """Switch the mascot's emotion and repaint."""
        self._state = state
        self.update()

    @property
    def state(self) -> MascotState:
        return self._state

    # ── Blink logic ───────────────────────────────────────────────────────────

    def _start_blink(self) -> None:
        self._is_blinking = True
        self._blink_frame = 0
        self._blink_anim_timer.start()

    def _advance_blink(self) -> None:
        self._blink_frame += 1
        self.update()
        if self._blink_frame >= 4:
            self._blink_anim_timer.stop()
            self._is_blinking = False
            self._blink_frame = 0
            self.blink_done.emit()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        cx = w / 2  # horizontal centre

        # ── 1. Drop body ──────────────────────────────────────────────────────
        self._draw_body(painter, w, h)

        # ── 2. Specular highlight ─────────────────────────────────────────────
        self._draw_highlight(painter, w, h)

        # ── 3. Face ───────────────────────────────────────────────────────────
        self._draw_face(painter, w, h)

        painter.end()

    def _drop_path(self, w: float, h: float) -> QPainterPath:
        """
        Build a teardrop / water-drop shape.

        The shape is a rounded bottom half (circle) with a pointed top.
        """
        path = QPainterPath()
        margin = w * 0.05
        # Start at top tip
        tip_x = w / 2
        tip_y = margin

        # Control points for the two sides
        left_cp1 = QPointF(margin, h * 0.25)
        left_cp2 = QPointF(margin, h * 0.55)
        right_cp1 = QPointF(w - margin, h * 0.25)
        right_cp2 = QPointF(w - margin, h * 0.55)

        # Bottom-left arc end
        bot_left = QPointF(margin, h * 0.68)
        # Bottom-right arc end
        bot_right = QPointF(w - margin, h * 0.68)

        path.moveTo(tip_x, tip_y)
        path.cubicTo(right_cp1, right_cp2, bot_right)

        # Bottom semicircle
        rect = QRectF(margin, h * 0.55, w - 2 * margin, (h - margin) - h * 0.55)
        path.arcTo(rect, 0, -180)

        path.cubicTo(left_cp2, left_cp1, QPointF(tip_x, tip_y))
        path.closeSubpath()
        return path

    def _draw_body(self, painter: QPainter, w: float, h: float) -> None:
        """Fill the drop body with a beautiful blue gradient."""
        path = self._drop_path(w, h)

        # Colour varies with emotional state
        if self._state == MascotState.HAPPY:
            top_color = QColor("#64DFDF")
            bot_color = QColor("#2196F3")
        elif self._state == MascotState.SAD:
            top_color = QColor("#78909C")
            bot_color = QColor("#37474F")
        else:
            top_color = QColor("#81D4FA")
            bot_color = QColor("#1565C0")

        grad = QLinearGradient(w / 2, 0, w / 2, h)
        grad.setColorAt(0.0, top_color)
        grad.setColorAt(1.0, bot_color)

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Outer glow / border
        glow_color = QColor(top_color)
        glow_color.setAlpha(180)
        pen = QPen(glow_color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def _draw_highlight(self, painter: QPainter, w: float, h: float) -> None:
        """Draw a small white specular blob in the top-right area."""
        hl_x = w * 0.62
        hl_y = h * 0.15
        hl_w = w * 0.15
        hl_h = h * 0.10

        grad = QRadialGradient(hl_x + hl_w / 2, hl_y + hl_h / 2, hl_w)
        grad.setColorAt(0.0, QColor(255, 255, 255, 200))
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(hl_x, hl_y, hl_w, hl_h))

    def _draw_face(self, painter: QPainter, w: float, h: float) -> None:
        """Draw eyes, expression, and optional blush."""
        # Eye vertical position
        eye_y = h * 0.48
        eye_left_x = w * 0.34
        eye_right_x = w * 0.66
        eye_rx = w * 0.055
        eye_ry = h * 0.065

        # Blink eye height multiplier
        blink_scale = self._blink_scale()

        eye_color = QColor("#1A1A2E")

        # Left eye
        self._draw_eye(painter, eye_left_x, eye_y, eye_rx, eye_ry * blink_scale, eye_color)
        # Right eye
        self._draw_eye(painter, eye_right_x, eye_y, eye_rx, eye_ry * blink_scale, eye_color)

        # Eye shine (small white dot)
        if blink_scale > 0.3:
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.setPen(Qt.NoPen)
            shine_r = w * 0.018
            painter.drawEllipse(
                QRectF(eye_left_x - eye_rx * 0.25, eye_y - eye_ry * blink_scale * 0.3, shine_r, shine_r)
            )
            painter.drawEllipse(
                QRectF(eye_right_x - eye_rx * 0.25, eye_y - eye_ry * blink_scale * 0.3, shine_r, shine_r)
            )

        # Mouth
        self._draw_mouth(painter, w, h)

        # Blush circles (HAPPY state)
        if self._state == MascotState.HAPPY:
            self._draw_blush(painter, w, h)

    def _draw_eye(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        color: QColor,
    ) -> None:
        """Draw a single eye ellipse centred on (cx, cy)."""
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        ry = max(ry, 0.5)
        painter.drawEllipse(QRectF(cx - rx, cy - ry, 2 * rx, 2 * ry))

    def _draw_mouth(self, painter: QPainter, w: float, h: float) -> None:
        """Draw a smile, neutral, or sad mouth depending on state."""
        mouth_y = h * 0.63
        mouth_cx = w * 0.50
        mouth_w = w * 0.28

        pen = QPen(QColor("#1A1A2E"), 2.5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        if self._state == MascotState.HAPPY:
            # Wide, upward arc
            path.moveTo(mouth_cx - mouth_w / 2, mouth_y - h * 0.01)
            path.quadTo(
                QPointF(mouth_cx, mouth_y + h * 0.06),
                QPointF(mouth_cx + mouth_w / 2, mouth_y - h * 0.01),
            )
        elif self._state == MascotState.SAD:
            # Downward arc
            path.moveTo(mouth_cx - mouth_w / 2, mouth_y + h * 0.02)
            path.quadTo(
                QPointF(mouth_cx, mouth_y - h * 0.04),
                QPointF(mouth_cx + mouth_w / 2, mouth_y + h * 0.02),
            )
        else:
            # Gentle smile
            path.moveTo(mouth_cx - mouth_w / 2, mouth_y)
            path.quadTo(
                QPointF(mouth_cx, mouth_y + h * 0.04),
                QPointF(mouth_cx + mouth_w / 2, mouth_y),
            )
        painter.drawPath(path)

    def _draw_blush(self, painter: QPainter, w: float, h: float) -> None:
        """Draw rosy cheeks in HAPPY state."""
        blush_y = h * 0.555
        blush_rx = w * 0.10
        blush_ry = h * 0.045

        blush = QColor(255, 120, 120, 100)
        painter.setBrush(blush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(w * 0.14, blush_y - blush_ry, 2 * blush_rx, 2 * blush_ry))
        painter.drawEllipse(QRectF(w * 0.76 - 2 * blush_rx, blush_y - blush_ry, 2 * blush_rx, 2 * blush_ry))

    def _blink_scale(self) -> float:
        """
        Return vertical scale for eyes during blink animation.
        frame: 0→open, 1→half, 2→closed, 3→half
        """
        if not self._is_blinking:
            return 1.0
        scales = [1.0, 0.35, 0.05, 0.35]
        return scales[min(self._blink_frame, 3)]
