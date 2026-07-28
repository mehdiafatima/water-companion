"""
setup_window.py
===============
First-run (and settings) window for Water Companion.

Shown when the app launches for the first time or when the user
selects "Open" or "Change Interval" from the tray menu.
"""

from __future__ import annotations

import math
from typing import Callable

from PySide6.QtCore import Qt, Signal, QPointF, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QIcon,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from water_companion.mascot.water_drop_widget import WaterDropWidget, MascotState
from water_companion.settings.config import AppConfig, save_config
from water_companion.ui.styles import SETUP_WINDOW_STYLE
from water_companion.utils.constants import (
    APP_NAME,
    APP_VERSION,
    INTERVAL_OPTIONS,
    DEFAULT_INTERVAL_LABEL,
    MASCOT_SIZE,
)
from water_companion.utils.logger import get_logger

log = get_logger(__name__)

# Ordered list for combo box display
INTERVAL_LABELS: list[str] = list(INTERVAL_OPTIONS.keys())


class SetupWindow(QWidget):
    """
    The main setup / first-run window.

    Signals
    -------
    start_requested(int) : Emitted with chosen interval in minutes when user clicks Start.
    """

    start_requested = Signal(int)

    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._apply_styles()
        log.info("SetupWindow initialised.")

    # ── UI Construction ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setObjectName("SetupWindow")
        self.setWindowTitle(f"{APP_NAME} — Setup")
        self.setFixedSize(420, 580)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Centre on screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 36, 30, 28)
        root.setSpacing(0)

        # ── Mascot ────────────────────────────────────────────────────────────
        mascot_row = QHBoxLayout()
        mascot_row.addStretch()
        self._mascot = WaterDropWidget(self)
        self._mascot.setFixedSize(MASCOT_SIZE, MASCOT_SIZE)
        mascot_row.addWidget(self._mascot)
        mascot_row.addStretch()
        root.addLayout(mascot_row)
        root.addSpacing(16)

        # ── Title ─────────────────────────────────────────────────────────────
        title = QLabel("💧 Water Companion")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)
        root.addSpacing(6)

        subtitle = QLabel("Your friendly hydration buddy")
        subtitle.setObjectName("AppSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        root.addWidget(subtitle)
        root.addSpacing(36)

        # ── Interval selector ─────────────────────────────────────────────────
        interval_label = QLabel("REMINDER INTERVAL")
        interval_label.setObjectName("SectionLabel")
        interval_label.setAlignment(Qt.AlignLeft)
        root.addWidget(interval_label)
        root.addSpacing(8)

        self._interval_combo = QComboBox()
        self._interval_combo.setObjectName("IntervalCombo")
        self._interval_combo.addItems(INTERVAL_LABELS)
        self._interval_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Pre-select stored interval
        stored_label = self._minutes_to_label(self._config.interval_minutes)
        idx = self._interval_combo.findText(stored_label)
        self._interval_combo.setCurrentIndex(max(idx, 0))
        root.addWidget(self._interval_combo)
        root.addSpacing(12)

        # ── Info card ─────────────────────────────────────────────────────────
        info = QLabel(
            "⏰  A gentle reminder will appear at the chosen interval.\n"
            "The app will keep running quietly in your system tray."
        )
        info.setObjectName("SectionLabel")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #546E7A; font-size: 12px;")
        root.addWidget(info)

        root.addStretch()

        # ── Start button ──────────────────────────────────────────────────────
        self._start_btn = QPushButton("💧  Start Reminder")
        self._start_btn.setObjectName("StartButton")
        self._start_btn.setFixedHeight(50)
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start_clicked)
        root.addWidget(self._start_btn)
        root.addSpacing(14)

        # ── Version ───────────────────────────────────────────────────────────
        ver = QLabel(f"v{APP_VERSION}")
        ver.setObjectName("VersionLabel")
        ver.setAlignment(Qt.AlignCenter)
        root.addWidget(ver)

        # Drag support (frameless window)
        self._drag_pos: QPointF | None = None

    def _apply_styles(self) -> None:
        self.setStyleSheet(SETUP_WINDOW_STYLE)

    # ── Painting (glass card background) ─────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Outer glow
        glow_path = QPainterPath()
        glow_path.addRoundedRect(4, 4, w - 8, h - 8, 24, 24)
        glow_color = QColor(79, 195, 247, 30)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow_color)
        painter.drawPath(glow_path)

        # Main card
        card_path = QPainterPath()
        card_path.addRoundedRect(8, 8, w - 16, h - 16, 20, 20)

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#0D1B2A"))
        grad.setColorAt(0.5, QColor("#0A1628"))
        grad.setColorAt(1.0, QColor("#060D18"))
        painter.setBrush(QBrush(grad))
        painter.drawPath(card_path)

        # Top accent line
        accent_grad = QLinearGradient(w * 0.2, 0, w * 0.8, 0)
        accent_grad.setColorAt(0.0, QColor(79, 195, 247, 0))
        accent_grad.setColorAt(0.5, QColor(79, 195, 247, 200))
        accent_grad.setColorAt(1.0, QColor(79, 195, 247, 0))
        from PySide6.QtGui import QPen
        painter.setPen(QPen(QBrush(accent_grad), 1.5))
        painter.drawLine(int(w * 0.1), 9, int(w * 0.9), 9)

        painter.end()

    # ── Drag support ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPosition() - self._drag_pos
            self.move(
                self.x() + int(delta.x()),
                self.y() + int(delta.y()),
            )
            self._drag_pos = event.globalPosition()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_pos = None

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_start_clicked(self) -> None:
        label = self._interval_combo.currentText()
        minutes = INTERVAL_OPTIONS.get(label, 30)

        # Save the selected interval
        self._config.interval_minutes = minutes
        self._config.first_run = False
        save_config(self._config)

        log.info("User selected interval: %s (%d min).", label, minutes)
        self.start_requested.emit(minutes)
        self.hide()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _minutes_to_label(minutes: int) -> str:
        """Find the combo label matching the given minute count."""
        for label, m in INTERVAL_OPTIONS.items():
            if m == minutes:
                return label
        return DEFAULT_INTERVAL_LABEL

    def update_interval_display(self, minutes: int) -> None:
        """Called externally when the interval changes (e.g. from tray menu)."""
        label = self._minutes_to_label(minutes)
        idx = self._interval_combo.findText(label)
        if idx >= 0:
            self._interval_combo.setCurrentIndex(idx)

    def show_window(self) -> None:
        """Bring the window to front."""
        self.show()
        self.raise_()
        self.activateWindow()
