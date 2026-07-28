"""
styles.py
=========
All Qt StyleSheets (QSS) for Water Companion.

Design System
-------------
- Background : #0A0E1A (deep navy)
- Surface     : #0D1B2A (dark panel)
- Card        : rgba(255,255,255,0.05) (glass)
- Primary     : #4FC3F7 (electric blue)
- Accent      : #81D4FA
- Success     : #69F0AE (mint green)
- Danger      : #FF8A80 (coral)
- Text        : #E0F7FA (light ice)
- Text Muted  : #78909C (grey-blue)
"""

# ─────────────────────────────────────────────────────────────────────────────
# Setup Window
# ─────────────────────────────────────────────────────────────────────────────

SETUP_WINDOW_STYLE = """
QWidget#SetupWindow {
    background: transparent;
}

QLabel#AppTitle {
    color: #4FC3F7;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#AppSubtitle {
    color: #78909C;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 400;
}

QLabel#SectionLabel {
    color: #B0BEC5;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QComboBox#IntervalCombo {
    background: rgba(255, 255, 255, 0.07);
    color: #E0F7FA;
    border: 1.5px solid rgba(79, 195, 247, 0.4);
    border-radius: 12px;
    padding: 10px 18px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    min-height: 22px;
}

QComboBox#IntervalCombo:hover {
    border: 1.5px solid #4FC3F7;
    background: rgba(79, 195, 247, 0.1);
}

QComboBox#IntervalCombo::drop-down {
    border: none;
    width: 30px;
}

QComboBox#IntervalCombo::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background: #0D1B2A;
    color: #E0F7FA;
    border: 1.5px solid rgba(79, 195, 247, 0.4);
    border-radius: 8px;
    selection-background-color: rgba(79, 195, 247, 0.25);
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    padding: 4px;
}

QPushButton#StartButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1E88E5,
        stop:1 #4FC3F7
    );
    color: white;
    border: none;
    border-radius: 14px;
    padding: 13px 0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#StartButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #2196F3,
        stop:1 #81D4FA
    );
}

QPushButton#StartButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1565C0,
        stop:1 #1E88E5
    );
}

QLabel#VersionLabel {
    color: #37474F;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 11px;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Reminder Window
# ─────────────────────────────────────────────────────────────────────────────

REMINDER_WINDOW_STYLE = """
QWidget#ReminderWindow {
    background: transparent;
}

QLabel#ReminderTitle {
    color: #4FC3F7;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 18px;
    font-weight: 700;
}

QLabel#ReminderSubtitle {
    color: #B0BEC5;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 400;
}

QLabel#MessageLabel {
    color: #E0F7FA;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 8px;
}

QPushButton#YesButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00BFA5,
        stop:1 #69F0AE
    );
    color: #003329;
    border: none;
    border-radius: 12px;
    padding: 10px 0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#YesButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00E5CC,
        stop:1 #B9F6CA
    );
}

QPushButton#YesButton:pressed {
    background: #00897B;
    color: white;
}

QPushButton#NoButton {
    background: rgba(255, 138, 128, 0.15);
    color: #FF8A80;
    border: 1.5px solid rgba(255, 138, 128, 0.4);
    border-radius: 12px;
    padding: 10px 0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#NoButton:hover {
    background: rgba(255, 138, 128, 0.28);
    border-color: #FF8A80;
}

QPushButton#NoButton:pressed {
    background: rgba(255, 138, 128, 0.45);
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Status / Settings Window
# ─────────────────────────────────────────────────────────────────────────────

STATUS_WINDOW_STYLE = """
QLabel {
    color: #E0F7FA;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

QLabel#StatusTitle {
    color: #4FC3F7;
    font-size: 20px;
    font-weight: 700;
}

QLabel#StatusValue {
    color: #69F0AE;
    font-size: 15px;
    font-weight: 600;
}

QLabel#StatusMuted {
    color: #78909C;
    font-size: 12px;
}

QPushButton {
    background: rgba(79, 195, 247, 0.12);
    color: #4FC3F7;
    border: 1.5px solid rgba(79, 195, 247, 0.35);
    border-radius: 10px;
    padding: 8px 18px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background: rgba(79, 195, 247, 0.22);
    border-color: #4FC3F7;
}

QComboBox {
    background: rgba(255, 255, 255, 0.07);
    color: #E0F7FA;
    border: 1.5px solid rgba(79, 195, 247, 0.4);
    border-radius: 10px;
    padding: 8px 14px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}

QComboBox QAbstractItemView {
    background: #0D1B2A;
    color: #E0F7FA;
    border: 1.5px solid rgba(79, 195, 247, 0.4);
    selection-background-color: rgba(79, 195, 247, 0.25);
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    padding: 4px;
}
"""
