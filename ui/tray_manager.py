# -*- coding: utf-8 -*-
"""
Windows System Tray Management Module (QSystemTrayIcon).
"""

import os
from typing import Callable, Optional
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon

from core.config import get_resource_path, SUPPORTED_REFRESH_INTERVALS
from .styles import MENU_STYLE


class TrayManager:
    """Manages system tray icon, tooltips, toasts, and context menu."""

    def __init__(
        self,
        on_toggle_visibility: Callable[[], None],
        on_toggle_mode: Callable[[], None],
        on_toggle_lock: Callable[[], None],
        on_change_interval: Callable[[int], None],
        on_quit: Callable[[], None],
        on_open_settings: Optional[Callable[[], None]] = None,
        on_open_help: Optional[Callable[[], None]] = None,
        on_open_about: Optional[Callable[[], None]] = None,
        parent=None
    ):
        self.parent = parent
        self.on_toggle_visibility = on_toggle_visibility
        self.on_toggle_mode = on_toggle_mode
        self.on_toggle_lock = on_toggle_lock
        self.on_change_interval = on_change_interval
        self.on_quit = on_quit
        self.on_open_settings = on_open_settings
        self.on_open_help = on_open_help
        self.on_open_about = on_open_about

        self.tray_icon = QSystemTrayIcon(parent)
        self.has_shown_minimize_balloon = False

        self._init_icon()
        self._init_menu()
        self._connect_signals()
        self.tray_icon.show()

    def _init_icon(self):
        """Load application tray icon."""
        ico_file = get_resource_path("app_icon.ico")
        png_file = get_resource_path("app_icon.png")
        icon = None
        if os.path.exists(ico_file):
            icon = QIcon(ico_file)
        elif os.path.exists(png_file):
            icon = QIcon(png_file)
        elif self.parent and not self.parent.windowIcon().isNull():
            icon = self.parent.windowIcon()

        if icon and not icon.isNull():
            self.tray_icon.setIcon(icon)

        self.tray_icon.setToolTip("OpenCode Token 实时监控器")

    def _init_menu(self):
        """Construct system tray context menu."""
        self.menu = QMenu()
        self.menu.setStyleSheet(MENU_STYLE)

        self.act_toggle_vis = QAction("隐藏监控悬浮窗", self.menu)
        self.act_toggle_vis.triggered.connect(self.on_toggle_visibility)
        self.menu.addAction(self.act_toggle_vis)

        self.act_toggle_mode = QAction("收起为 1行迷你胶囊", self.menu)
        self.act_toggle_mode.triggered.connect(self.on_toggle_mode)
        self.menu.addAction(self.act_toggle_mode)

        self.act_lock = QAction("锁定位置 (防误触)", self.menu)
        self.act_lock.triggered.connect(self.on_toggle_lock)
        self.menu.addAction(self.act_lock)

        self.menu.addSeparator()

        # Refresh frequency submenu
        rate_menu = self.menu.addMenu("刷新频率")
        for ms, label in SUPPORTED_REFRESH_INTERVALS:
            act = QAction(label, self.menu)
            act.triggered.connect(lambda checked, m=ms: self.on_change_interval(m))
            rate_menu.addAction(act)

        # Settings
        if self.on_open_settings:
            act_settings = QAction("设置", self.menu)
            act_settings.triggered.connect(self.on_open_settings)
            self.menu.addAction(act_settings)

        # Help submenu (hover expands Help and About)
        help_menu = self.menu.addMenu("帮助")
        if self.on_open_help:
            act_help = QAction("帮助", self.menu)
            act_help.triggered.connect(self.on_open_help)
            help_menu.addAction(act_help)

        if self.on_open_about:
            act_about = QAction("关于", self.menu)
            act_about.triggered.connect(self.on_open_about)
            help_menu.addAction(act_about)

        self.menu.addSeparator()

        act_quit = QAction("退出监控程序", self.menu)
        act_quit.triggered.connect(self.on_quit)
        self.menu.addAction(act_quit)

        self.tray_icon.setContextMenu(self.menu)

    def _connect_signals(self):
        """Bind activation signals (support single and double click toggle)."""
        self.tray_icon.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.on_toggle_visibility()

    def set_window_visible_state(self, is_visible: bool):
        """Synchronize visibility menu item text."""
        self.act_toggle_vis.setText("隐藏监控悬浮窗" if is_visible else "显示监控悬浮窗")

    def set_mini_mode_state(self, is_mini: bool, row_count: int = 3):
        """Synchronize mini/full mode menu item text."""
        self.act_toggle_mode.setText(f"展开为 {row_count}行完整面板" if is_mini else "收起为 1行迷你胶囊")

    def set_lock_state(self, is_locked: bool):
        """Synchronize window lock menu item text."""
        self.act_lock.setText("解除锁定位置" if is_locked else "锁定位置 (防误触)")

    def update_tooltip(self, name: str, speed: str):
        """Update system tray hover tooltip dynamically."""
        self.tray_icon.setToolTip(f"OpenCode Token 监控器 v1.0\n当前: {name} | {speed}")

    def show_minimize_toast(self):
        """Display toast notification on first minimize to tray."""
        if not self.has_shown_minimize_balloon:
            self.has_shown_minimize_balloon = True
            self.tray_icon.showMessage(
                "OpenCode Token 监控器",
                "已最小化至任务栏右侧通知区域。点击托盘小图标可随时恢复悬浮窗。",
                QSystemTrayIcon.Information,
                2000
            )

    def hide(self):
        """Hide tray icon before app exit."""
        self.tray_icon.hide()
