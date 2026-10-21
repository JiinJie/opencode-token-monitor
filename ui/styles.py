# -*- coding: utf-8 -*-
"""
UI stylesheets (QSS), palettes, and visual theme constants.
"""

# Main background card style (translucent dark glassmorphism capsule)
CARD_STYLE = """
QFrame#mainCard {
    background-color: rgba(18, 20, 26, 238);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
}
"""

# Right-click context menu and system tray menu style
MENU_STYLE = """
QMenu {
    background-color: #1A1D24;
    color: #F3F4F6;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 4px;
    font-family: 'Segoe UI', 'Microsoft YaHei';
    font-size: 12px;
}
QMenu::item {
    padding: 6px 22px 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #2563EB;
}
QMenu::separator {
    height: 1px;
    background-color: #374151;
    margin: 4px 6px;
}
"""

# Settings and About Dialog dark styling
DIALOG_STYLE = """
QDialog {
    background-color: #12141A;
    color: #F3F4F6;
    font-family: 'Segoe UI', 'Microsoft YaHei';
}
QFrame#dialogCard {
    background-color: #12141A;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}
QGroupBox {
    color: #00FFCC;
    font-size: 11px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    padding-bottom: 8px;
    padding-left: 10px;
    padding-right: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
    background-color: #12141A;
}
QLabel {
    color: #E2E8F0;
    font-size: 12px;
}
QLineEdit {
    background-color: #1A1D24;
    border: 1px solid #374151;
    border-radius: 6px;
    color: #F3F4F6;
    padding: 6px 10px;
    font-size: 12px;
    font-family: 'Consolas', 'Segoe UI';
}
QLineEdit:focus {
    border: 1px solid #00FFCC;
}
QPushButton {
    background-color: #262933;
    color: #F3F4F6;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #374151;
    border-color: #4B5563;
}
QPushButton:pressed {
    background-color: #1F222B;
}
QPushButton#primaryBtn {
    background-color: #059669;
    color: #FFFFFF;
    border: 1px solid #10B981;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background-color: #10B981;
}
QPushButton#dangerBtn {
    background-color: #7F1D1D;
    color: #FECACA;
    border: 1px solid #DC2626;
}
QPushButton#dangerBtn:hover {
    background-color: #991B1B;
}
QComboBox {
    background-color: #1A1D24;
    color: #F3F4F6;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
}
QComboBox QAbstractItemView {
    background-color: #1A1D24;
    color: #F3F4F6;
    selection-background-color: #2563EB;
    border: 1px solid #374151;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #272A34;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #00FFCC;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}
QCheckBox {
    color: #E2E8F0;
    font-size: 12px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #4B5563;
    border-radius: 4px;
    background-color: #1A1D24;
}
QCheckBox::indicator:checked {
    background-color: #10B981;
    border-color: #10B981;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #181A20;
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #374151;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #00FFCC;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Session status badge styling schemes
BADGE_STYLES = {
    "fg": {
        "text": "前台",
        "style": """
            background-color: rgba(16, 185, 129, 0.25);
            color: #10B981;
            border: 1px solid #10B981;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
        """
    },
    "fg_unfocused": {
        "text": "前台·挂起",
        "style": """
            background-color: rgba(245, 158, 11, 0.2);
            color: #F59E0B;
            border: 1px solid #F59E0B;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
        """
    },
    "bg": {
        "text": "后台",
        "style": """
            background-color: rgba(59, 130, 246, 0.2);
            color: #60A5FA;
            border: 1px solid #3B82F6;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
        """
    },
    "subagent": {
        "text": "子任务",
        "style": """
            background-color: rgba(168, 85, 247, 0.2);
            color: #C084FC;
            border: 1px solid #A855F7;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
        """
    },
    "idle": {
        "text": "待命",
        "style": """
            background-color: rgba(107, 114, 128, 0.2);
            color: #9CA3AF;
            border: 1px solid #6B7280;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
        """
    }
}
