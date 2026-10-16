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
