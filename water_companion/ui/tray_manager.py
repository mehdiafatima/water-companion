"""
tray_manager.py
===============
System tray icon and context menu for Water Companion.

The tray icon is drawn entirely in code via QPainter — no external icon files.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from water_companion.utils.constants import APP_NAME, INTERVAL_OPTIONS
from water_companion.utils.logger import get_logger

log = get_logger(__name__)


def _make_tray_icon(size: int = 64) -> QIcon:
    """
    Draw the tray icon completely in code.
    Compatible with PySide6 6.7+.
    """

    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    w = float(size)
    h = float(size)
    margin = w * 0.05

    # -----------------------------
    # Water drop shape
    # -----------------------------
    path = QPainterPath()

    tip_x = w / 2
    tip_y = margin

    path.moveTo(tip_x, tip_y)

    path.cubicTo(
        w - margin,
        h * 0.25,
        w - margin,
        h * 0.55,
        w - margin,
        h * 0.68,
    )

    arc = QRectF(
        margin,
        h * 0.55,
        w - (margin * 2),
        (h - margin) - (h * 0.55),
    )

    path.arcTo(arc, 0, -180)

    path.cubicTo(
        margin,
        h * 0.55,
        margin,
        h * 0.25,
        tip_x,
        tip_y,
    )

    path.closeSubpath()

    gradient = QLinearGradient(w / 2, 0, w / 2, h)
    gradient.setColorAt(0.0, QColor("#81D4FA"))
    gradient.setColorAt(1.0, QColor("#1565C0"))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawPath(path)

    # -----------------------------
    # Eyes
    # -----------------------------
    painter.setBrush(QColor("#1A1A2E"))

    eye_y = h * 0.50
    eye_radius = w * 0.06

    painter.drawEllipse(
        QRectF(
            w * 0.32 - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )
    )

    painter.drawEllipse(
        QRectF(
            w * 0.68 - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )
    )

    painter.end()

    # -----------------------------
    # IMPORTANT FIX
    # -----------------------------
    pixmap = QPixmap.fromImage(image)

    pixmap = pixmap.scaled(
        QSize(size, size),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    return QIcon(pixmap)


class TrayManager(QObject):
    """
    System tray manager.
    """

    open_requested = Signal()
    pause_requested = Signal()
    resume_requested = Signal()
    interval_changed = Signal(int)
    quit_requested = Signal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._icon = _make_tray_icon()

        self._tray = QSystemTrayIcon(self._icon, self)
        self._tray.setToolTip(APP_NAME)

        self._build_menu()

        self._tray.activated.connect(self._on_tray_activated)

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def show(self):
        self._tray.show()
        log.info("Tray icon shown.")

    def hide(self):
        self._tray.hide()

    def set_paused(self, paused: bool):
        self._pause_action.setEnabled(not paused)
        self._resume_action.setEnabled(paused)

    def show_message(
        self,
        title: str,
        message: str,
        duration_ms: int = 3000,
    ):
        self._tray.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            duration_ms,
        )

    # -------------------------------------------------
    # Menu
    # -------------------------------------------------

    def _build_menu(self):

        menu = QMenu()

        menu.setStyleSheet(
            """
            QMenu {
                background:#0D1B2A;
                color:#E0F7FA;
                border:1px solid rgba(79,195,247,.25);
                border-radius:8px;
                font-size:13px;
                padding:4px;
            }

            QMenu::item{
                padding:7px 22px;
            }

            QMenu::item:selected{
                background:rgba(79,195,247,.18);
                color:#4FC3F7;
            }

            QMenu::separator{
                height:1px;
                background:rgba(79,195,247,.15);
                margin:4px 10px;
            }
            """
        )

        # Open
        action = QAction("💧 Open Water Companion", self)
        action.triggered.connect(self.open_requested.emit)
        menu.addAction(action)

        menu.addSeparator()

        # Pause
        self._pause_action = QAction("⏸ Pause Reminders", self)
        self._pause_action.triggered.connect(
            self.pause_requested.emit
        )
        menu.addAction(self._pause_action)

        # Resume
        self._resume_action = QAction("▶ Resume Reminders", self)
        self._resume_action.setEnabled(False)
        self._resume_action.triggered.connect(
            self.resume_requested.emit
        )
        menu.addAction(self._resume_action)

        menu.addSeparator()

        interval_menu = QMenu("⏱ Change Interval", menu)
        interval_menu.setStyleSheet(menu.styleSheet())

        for label, minutes in INTERVAL_OPTIONS.items():
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False, m=minutes: self.interval_changed.emit(m)
            )
            interval_menu.addAction(action)

        menu.addMenu(interval_menu)

        menu.addSeparator()

        quit_action = QAction("✕ Quit", self)
        quit_action.triggered.connect(
            self.quit_requested.emit
        )
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)

    # -------------------------------------------------
    # Tray events
    # -------------------------------------------------

    def _on_tray_activated(
        self,
        reason: QSystemTrayIcon.ActivationReason,
    ):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_requested.emit()