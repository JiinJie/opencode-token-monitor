# -*- coding: utf-8 -*-
"""
OpenCode Real-time Token Speed & Usage Floating Main Panel.
"""

import os
from typing import List
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QMenu, QAction, QApplication
)
from PyQt5.QtGui import QCursor, QIcon, QDesktopServices

from core.config import (
    DEFAULT_REFRESH_INTERVAL_MS,
    SUPPORTED_REFRESH_INTERVALS,
    PROJECT_GITHUB,
    AppSettings,
    get_resource_path
)
from core.telemetry import OpenCodeTelemetry
from core.models import MonitorState

from .styles import CARD_STYLE, MENU_STYLE
from .session_row import SessionRowWidget
from .tray_manager import TrayManager
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog


class OpenCodeTokenMonitor(QWidget):
    """OpenCode Real-time Token Speed and Usage Floating Widget (Foreground/Background session support)."""

    def __init__(self, db_path: str = None, refresh_interval: int = DEFAULT_REFRESH_INTERVAL_MS):
        super().__init__()
        self.drag_position = QPoint()
        self.mini_mode = False
        self.locked = False

        # Load configuration (maintaining exact original defaults)
        self.settings = AppSettings.load()
        if db_path:
            self.settings.db_path = db_path
        if refresh_interval is not None:
            self.settings.refresh_interval_ms = refresh_interval

        self.refresh_interval = self.settings.refresh_interval_ms or DEFAULT_REFRESH_INTERVAL_MS

        # Telemetry core engine
        self.telemetry = OpenCodeTelemetry(
            db_path=self.settings.db_path,
            enable_anti_burst=self.settings.enable_anti_burst,
            enable_ttft=self.settings.enable_ttft
        )

        self.rows: List[SessionRowWidget] = []
        self._init_ui()
        self._init_tray()

        # Polling timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(self.refresh_interval)

        # Initial refresh
        self.refresh_metrics()

    def _init_ui(self):
        """Initialize window geometry, flags, and layout (strictly preserving original style)."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Set application icon
        ico_file = get_resource_path("app_icon.ico")
        png_file = get_resource_path("app_icon.png")
        app_icon = None
        if os.path.exists(ico_file):
            app_icon = QIcon(ico_file)
        elif os.path.exists(png_file):
            app_icon = QIcon(png_file)
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        # Root layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Main background card container
        self.card = QFrame(self)
        self.card.setObjectName("mainCard")
        self.card.setStyleSheet(CARD_STYLE)
        root_layout.addWidget(self.card)

        # Card inner vertical layout
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(10, 8, 10, 8)
        self.card_layout.setSpacing(4)

        # Top minimal header bar
        self.header = QWidget(self.card)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(4, 0, 4, 2)

        title_icon = QLabel("⚡", self.header)
        title_icon.setStyleSheet("color: #00FFCC; font-size: 11px; font-weight: bold;")
        header_layout.addWidget(title_icon)

        self.title_label = QLabel("OpenCode 监控 v1.0", self.header)
        self.title_label.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: 600; font-family: 'Segoe UI', 'Microsoft YaHei';")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Mini mode toggle button
        self.mode_btn = QLabel("–", self.header)
        self.mode_btn.setCursor(Qt.PointingHandCursor)
        self.mode_btn.setStyleSheet("color: #64748B; font-size: 13px; font-weight: bold; padding: 0 4px;")
        self.mode_btn.setToolTip("双击面板或点击此处切换 单行/三行 模式")
        self.mode_btn.mousePressEvent = lambda e: self.toggle_mini_mode()
        header_layout.addWidget(self.mode_btn)

        # Close button (minimizes to system tray by default)
        close_btn = QLabel("✕", self.header)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("color: #64748B; font-size: 11px; padding: 0 4px;")
        close_btn.setToolTip("最小化至系统托盘 (右键托盘图标可退出)")
        close_btn.mousePressEvent = lambda e: self.hide_to_tray()
        header_layout.addWidget(close_btn)

        self.card_layout.addWidget(self.header)

        # Create 3 display rows
        for i in range(3):
            row_widget = SessionRowWidget(i, self.card)
            self.rows.append(row_widget)
            self.card_layout.addWidget(row_widget)

        self.adjustSize()

        # Default position: top right of primary screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.sizeHint().width() - 35, 45)

    def _init_tray(self):
        """Initialize system tray integration."""
        self.tray = TrayManager(
            on_toggle_visibility=self.toggle_visibility,
            on_toggle_mode=self.toggle_mini_mode,
            on_toggle_lock=self.toggle_lock,
            on_change_interval=self.set_refresh_rate,
            on_quit=self.quit_app,
            on_open_settings=self.open_settings,
            on_open_help=self.open_help_url,
            on_open_about=self.open_about_dialog,
            parent=self
        )

    def refresh_metrics(self):
        """Core data polling and metric dispatch engine."""
        state: MonitorState = self.telemetry.collect()

        if not state.db_exists:
            self.rows[0].update_data("idle", "[无库]", "未找到OpenCode库", "0.0 tok/s", "#6B7280", "请检查路径")
            return

        if not state.foreground_session:
            self.rows[0].update_data("idle", "[待命]", "无活跃会话", "-- tok/s", "#6B7280", "等待任务")
            return

        # 1. Render Row 0: Active foreground session
        self.rows[0].render_session(
            state.foreground_session,
            is_foreground_row=True,
            is_focused=state.is_opencode_foreground,
            fg_info=state.foreground_info
        )

        # 2. Render Rows 1 and 2: Recent background sessions
        for i in range(1, 3):
            idx = i - 1
            if idx < len(state.other_sessions):
                self.rows[i].render_session(state.other_sessions[idx], is_foreground_row=False)
            else:
                self.rows[i].update_data("idle", "[待命]", "无更多会话", "-- tok/s", "#6B7280", "等待任务")

        self.adjustSize()

        # 3. Synchronize tray tooltip
        try:
            fg_speed = self.rows[0].speed_label.text()
            fg_name = self.rows[0].name_label.text()
            self.tray.update_tooltip(fg_name, fg_speed)
        except Exception:
            pass

    def toggle_visibility(self):
        """Toggle floating window visibility while maintaining always-on-top order."""
        if self.isVisible():
            self.hide()
            self.tray.set_window_visible_state(False)
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.tray.set_window_visible_state(True)

    def hide_to_tray(self):
        """Minimize to system notification tray."""
        self.hide()
        self.tray.set_window_visible_state(False)
        self.tray.show_minimize_toast()

    def toggle_mini_mode(self):
        """Toggle between 1-row mini capsule and 3-row full panel."""
        self.mini_mode = not self.mini_mode
        self.header.setVisible(not self.mini_mode)
        self.rows[1].setVisible(not self.mini_mode)
        self.rows[2].setVisible(not self.mini_mode)
        self.mode_btn.setText("+" if self.mini_mode else "–")
        self.tray.set_mini_mode_state(self.mini_mode)
        self.setMinimumSize(0, 0)
        self.adjustSize()

    def toggle_lock(self):
        """Toggle position dragging lock."""
        self.locked = not self.locked
        self.settings.locked = self.locked
        self.settings.save()
        self.tray.set_lock_state(self.locked)

    def set_refresh_rate(self, ms: int):
        """Update polling frequency interval."""
        valid_ms = ms or DEFAULT_REFRESH_INTERVAL_MS
        self.refresh_interval = valid_ms
        self.settings.refresh_interval_ms = valid_ms
        self.settings.save()
        self.timer.setInterval(valid_ms)

    def open_settings(self):
        """Open Settings preferences dialog."""
        dialog = SettingsDialog(
            current_settings=self.settings,
            on_apply_callback=self.apply_settings,
            parent=self
        )
        dialog.exec_()

    def apply_settings(self, new_settings: AppSettings):
        """Dynamically apply updated settings without modifying main window visual styles."""
        self.settings = new_settings
        self.refresh_interval = self.settings.refresh_interval_ms
        self.timer.setInterval(self.refresh_interval)

        # Update telemetry parameters
        self.telemetry.db_path = self.settings.db_path
        self.telemetry.enable_anti_burst = self.settings.enable_anti_burst
        self.telemetry.enable_ttft = self.settings.enable_ttft

        self.refresh_metrics()

    def open_help_url(self):
        """Open project GitHub repository in user's default browser."""
        QDesktopServices.openUrl(QUrl(PROJECT_GITHUB))

    def open_about_dialog(self):
        """Open About modal dialog."""
        dialog = AboutDialog(parent=self)
        dialog.exec_()

    def quit_app(self):
        """Safely terminate the application."""
        self.tray.hide()
        QApplication.instance().quit()

    # Mouse drag handlers
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.locked:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.locked:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_mini_mode()
            event.accept()

    # Context menu handler
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)

        mode_text = "展开为 3行完整面板" if self.mini_mode else "收起为 1行迷你胶囊"
        toggle_mode_act = QAction(mode_text, self)
        toggle_mode_act.triggered.connect(self.toggle_mini_mode)
        menu.addAction(toggle_mode_act)

        lock_text = "解除锁定位置" if self.locked else "锁定位置 (防误触)"
        lock_act = QAction(lock_text, self)
        lock_act.triggered.connect(self.toggle_lock)
        menu.addAction(lock_act)

        menu.addSeparator()

        rate_menu = menu.addMenu("刷新频率")
        for ms, label in SUPPORTED_REFRESH_INTERVALS:
            act = QAction(label, self)
            if self.refresh_interval == ms:
                act.setText("✔ " + label)
            act.triggered.connect(lambda checked, m=ms: self.set_refresh_rate(m))
            rate_menu.addAction(act)

        # 需求一：在刷新频率下方增加“设置”
        settings_act = QAction("设置", self)
        settings_act.triggered.connect(self.open_settings)
        menu.addAction(settings_act)

        # 需求二：在设置下方增加“帮助”，鼠标悬停显示“帮助”和“关于”
        help_menu = menu.addMenu("帮助")

        help_doc_act = QAction("帮助", self)
        help_doc_act.triggered.connect(self.open_help_url)
        help_menu.addAction(help_doc_act)

        about_act = QAction("关于", self)
        about_act.triggered.connect(self.open_about_dialog)
        help_menu.addAction(about_act)

        menu.addSeparator()

        hide_act = QAction("最小化到系统托盘", self)
        hide_act.triggered.connect(self.hide_to_tray)
        menu.addAction(hide_act)

        quit_act = QAction("退出监控程序", self)
        quit_act.triggered.connect(self.quit_app)
        menu.addAction(quit_act)

        menu.exec_(QCursor.pos())
