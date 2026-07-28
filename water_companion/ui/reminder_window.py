"""
reminder_window.py
==================
The floating reminder popup window — the heart of Water Companion.

Flow
----
1. show_reminder() is called by ReminderManager signal.
2. Mascot slides in from below.
3. Mascot begins floating animation.
4. User clicks Yes or No.
5. Particles spawn.
6. Mascot slides out.
7. responded signal emitted → caller restarts timer.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QPoint,
    QPropertyAnimation,
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
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from water_companion.core.messages import (
    get_encouragement_message,
    get_gentle_reminder,
    get_reminder_subtitle,
)
from water_companion.mascot.animations import (
    FloatAnimator,
    make_slide_in_animation,
    make_slide_out_animation,
    spawn_happy_particles,
    spawn_sad_particles,
)
from water_companion.mascot.water_drop_widget import MascotState, WaterDropWidget
from water_companion.ui.styles import REMINDER_WINDOW_STYLE
from water_companion.utils.constants import MASCOT_SIZE, REMINDER_WINDOW_HEIGHT, REMINDER_WINDOW_WIDTH
from water_companion.utils.logger import get_logger

log = get_logger(__name__)


class ReminderWindow(QWidget):
    """
    Frameless, always-on-top reminder popup.

    Signals
    -------
    responded(bool) : True if user clicked Yes, False if No.
    """

    responded = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._float_animator: FloatAnimator | None = None
        self._slide_in_anim: QPropertyAnimation | None = None
        self._slide_out_anim: QPropertyAnimation | None = None
        self._setup_ui()
        self._apply_styles()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setObjectName("ReminderWindow")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool                  # Don't show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(REMINDER_WINDOW_WIDTH, REMINDER_WINDOW_HEIGHT)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 22, 20, 20)
        root.setSpacing(0)

        # ── Mascot ────────────────────────────────────────────────────────────
        mascot_row = QHBoxLayout()
        mascot_row.addStretch()
        self._mascot = WaterDropWidget(self)
        self._mascot.setFixedSize(MASCOT_SIZE, MASCOT_SIZE)
        mascot_row.addWidget(self._mascot)
        mascot_row.addStretch()
        root.addLayout(mascot_row)
        root.addSpacing(12)

        # ── Title ─────────────────────────────────────────────────────────────
        self._title_label = QLabel("💧 Time to Hydrate!")
        self._title_label.setObjectName("ReminderTitle")
        self._title_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self._title_label)
        root.addSpacing(4)

        self._subtitle_label = QLabel("Have you drunk water?")
        self._subtitle_label.setObjectName("ReminderSubtitle")
        self._subtitle_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self._subtitle_label)
        root.addSpacing(16)

        # ── Response message ──────────────────────────────────────────────────
        self._message_label = QLabel("")
        self._message_label.setObjectName("MessageLabel")
        self._message_label.setAlignment(Qt.AlignCenter)
        self._message_label.setWordWrap(True)
        self._message_label.setFixedHeight(44)
        root.addWidget(self._message_label)
        root.addSpacing(10)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._yes_btn = QPushButton("✅  Yes!")
        self._yes_btn.setObjectName("YesButton")
        self._yes_btn.setCursor(Qt.PointingHandCursor)
        self._yes_btn.setFixedHeight(44)
        self._yes_btn.clicked.connect(self._on_yes)

        self._no_btn = QPushButton("❌  Not Yet")
        self._no_btn.setObjectName("NoButton")
        self._no_btn.setCursor(Qt.PointingHandCursor)
        self._no_btn.setFixedHeight(44)
        self._no_btn.clicked.connect(self._on_no)

        btn_row.addWidget(self._yes_btn)
        btn_row.addWidget(self._no_btn)
        root.addLayout(btn_row)

    def _apply_styles(self) -> None:
        self.setStyleSheet(REMINDER_WINDOW_STYLE)

    # ── Paint (glass card) ────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Glow ring
        glow = QPainterPath()
        glow.addRoundedRect(2, 2, w - 4, h - 4, 22, 22)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(79, 195, 247, 25))
        painter.drawPath(glow)

        # Card body
        card = QPainterPath()
        card.addRoundedRect(6, 6, w - 12, h - 12, 18, 18)

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#0E1E30"))
        grad.setColorAt(1.0, QColor("#060D18"))
        painter.setBrush(QBrush(grad))
        painter.drawPath(card)

        # Border
        border_grad = QLinearGradient(0, 0, 0, h)
        border_grad.setColorAt(0.0, QColor(79, 195, 247, 120))
        border_grad.setColorAt(1.0, QColor(79, 195, 247, 30))
        painter.setPen(QPen(QBrush(border_grad), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(card)

        painter.end()

    # ── Public interface ──────────────────────────────────────────────────────

    def show_reminder(self) -> None:
        """
        Trigger the full entrance sequence:
        place off-screen → slide in → start floating.
        """
        # Reset state
        self._message_label.setText("")
        self._mascot.set_state(MascotState.NORMAL)
        self._yes_btn.setEnabled(True)
        self._no_btn.setEnabled(True)
        self._subtitle_label.setText(get_reminder_subtitle())

        # Position off-screen initially
        screen = QApplication.primaryScreen().availableGeometry()
        from water_companion.utils.constants import REMINDER_WINDOW_WIDTH, REMINDER_WINDOW_HEIGHT, TRAY_MARGIN_PX
        target_x = screen.right() - REMINDER_WINDOW_WIDTH - TRAY_MARGIN_PX
        self.move(target_x, screen.bottom() + 10)
        self.show()
        self.raise_()

        # Slide in
        self._slide_in_anim = make_slide_in_animation(self, screen)
        self._slide_in_anim.finished.connect(self._on_slide_in_done)
        self._slide_in_anim.start()

        log.info("Reminder window shown.")

    # ── Internal flow ─────────────────────────────────────────────────────────

    def _on_slide_in_done(self) -> None:
        """Start floating after slide-in completes."""
        self._float_animator = FloatAnimator(self, self)
        self._float_animator.start()

    def _on_yes(self) -> None:
        self._yes_btn.setEnabled(False)
        self._no_btn.setEnabled(False)
        self._mascot.set_state(MascotState.HAPPY)
        self._message_label.setText(get_encouragement_message())

        # Particle origin = mascot centre in window-local coords
        mascot_centre = QPoint(
            self._mascot.x() + self._mascot.width() // 2,
            self._mascot.y() + self._mascot.height() // 2,
        )
        spawn_happy_particles(self, mascot_centre)

        # Slide out after a short appreciation delay
        QTimer.singleShot(1400, lambda: self._slide_out(responded=True))

    def _on_no(self) -> None:
        self._yes_btn.setEnabled(False)
        self._no_btn.setEnabled(False)
        self._mascot.set_state(MascotState.SAD)
        self._message_label.setText(get_gentle_reminder())

        mascot_centre = QPoint(
            self._mascot.x() + self._mascot.width() // 2,
            self._mascot.y() + self._mascot.height() // 2,
        )
        spawn_sad_particles(self, mascot_centre)

        QTimer.singleShot(1200, lambda: self._slide_out(responded=False))

    def _slide_out(self, responded: bool) -> None:
        """Animate the window sliding off-screen, then emit responded signal."""
        # Stop floating first
        if self._float_animator:
            self._float_animator.stop()
            self._float_animator = None

        screen = QApplication.primaryScreen().availableGeometry()
        self._slide_out_anim = make_slide_out_animation(self, screen)
        self._slide_out_anim.finished.connect(lambda: self._on_slide_out_done(responded))
        self._slide_out_anim.start()

    def _on_slide_out_done(self, responded: bool) -> None:
        self.hide()
        self.responded.emit(responded)
        log.info("Reminder dismissed. Responded: %s", responded)
