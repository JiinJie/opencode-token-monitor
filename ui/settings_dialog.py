# -*- coding: utf-8 -*-
"""
Application preferences and settings management dialog.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSlider, QCheckBox, QGroupBox,
    QFileDialog, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from core.config import (
    APP_NAME, DEFAULT_DB_PATH, DEFAULT_REFRESH_INTERVAL_MS,
    SUPPORTED_REFRESH_INTERVALS, AppSettings, get_resource_path
)
from .styles import DIALOG_STYLE


class SettingsDialog(QDialog):
    """Modern dark-themed preferences dialog."""

    def __init__(self, current_settings: AppSettings, on_apply_callback=None, parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.on_apply_callback = on_apply_callback

        self.setWindowTitle(f"设置 - {APP_NAME}")
        self.setFixedSize(520, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)

        self._init_ui()
        self._load_from_settings()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)

        card = QFrame(self)
        card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        # 1. Title bar
        title_box = QHBoxLayout()
        title_label = QLabel("⚙️ 监控与偏好设置", card)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        title_box.addWidget(title_label)
        title_box.addStretch()
        card_layout.addLayout(title_box)

        # 2. Group: Data Source (Database Path)
        group_db = QGroupBox("📂 遥测数据源 (OpenCode 数据库)", card)
        db_layout = QVBoxLayout(group_db)
        db_layout.setSpacing(6)

        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(group_db)
        self.path_edit.setPlaceholderText("请输入或选择 opencode.db 绝对路径...")
        self.path_edit.textChanged.connect(self._check_db_status)
        path_row.addWidget(self.path_edit)

        browse_btn = QPushButton("浏览...", group_db)
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_db_file)
        path_row.addWidget(browse_btn)

        reset_btn = QPushButton("重置", group_db)
        reset_btn.setFixedWidth(55)
        reset_btn.setToolTip("恢复为系统默认数据库路径")
        reset_btn.clicked.connect(self._reset_default_db)
        path_row.addWidget(reset_btn)
        db_layout.addLayout(path_row)

        self.db_status_label = QLabel("", group_db)
        self.db_status_label.setStyleSheet("font-size: 11px;")
        db_layout.addWidget(self.db_status_label)
        card_layout.addWidget(group_db)

        # 3. Group: Performance & Interval
        group_perf = QGroupBox("⚡ 性能与刷新频率", card)
        perf_layout = QHBoxLayout(group_perf)
        perf_layout.addWidget(QLabel("采样刷新间隔:", group_perf))
        self.interval_combo = QComboBox(group_perf)
        for ms, label in SUPPORTED_REFRESH_INTERVALS:
            self.interval_combo.addItem(label, ms)
        perf_layout.addWidget(self.interval_combo)
        perf_layout.addStretch()
        card_layout.addWidget(group_perf)

        # 4. Group: Appearance & Window Behavior
        group_ui = QGroupBox("🎨 界面与悬浮窗行为", card)
        ui_layout = QVBoxLayout(group_ui)
        ui_layout.setSpacing(8)

        # Startup mode & Opacity
        row_mode = QHBoxLayout()
        row_mode.addWidget(QLabel("启动默认形态:", group_ui))
        self.mode_combo = QComboBox(group_ui)
        self.mode_combo.addItem("3 行完整面板 (多任务/前后台感知)", False)
        self.mode_combo.addItem("1 行极简迷你胶囊 (紧凑省空间)", True)
        row_mode.addWidget(self.mode_combo)
        row_mode.addStretch()
        ui_layout.addLayout(row_mode)

        row_opacity = QHBoxLayout()
        row_opacity.addWidget(QLabel("窗口不透明度:", group_ui))
        self.opacity_slider = QSlider(Qt.Horizontal, group_ui)
        self.opacity_slider.setRange(70, 100)
        self.opacity_slider.setSingleStep(5)
        self.opacity_val_label = QLabel("95%", group_ui)
        self.opacity_val_label.setFixedWidth(38)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_val_label.setText(f"{v}%")
        )
        row_opacity.addWidget(self.opacity_slider)
        row_opacity.addWidget(self.opacity_val_label)
        ui_layout.addLayout(row_opacity)

        # Checkboxes for Topmost and Lock
        row_checks = QHBoxLayout()
        self.topmost_check = QCheckBox("始终保持置顶 (Always on top)", group_ui)
        self.lock_check = QCheckBox("锁定位置 (禁止拖拽)", group_ui)
        row_checks.addWidget(self.topmost_check)
        row_checks.addWidget(self.lock_check)
        ui_layout.addLayout(row_checks)
        card_layout.addWidget(group_ui)

        # 5. Group: Anti-Burst & TTFT Detection
        group_algo = QGroupBox("🛡️ 速率与延迟算法", card)
        algo_layout = QVBoxLayout(group_algo)
        algo_layout.setSpacing(6)

        self.anti_burst_check = QCheckBox("开启防整包突发虚标校准 (Anti-Burst Detection)", group_algo)
        self.anti_burst_check.setToolTip("遇到反代网关憋大招整包推送时，自动以真实体感速率校准，杜绝千Token/s虚标")
        algo_layout.addWidget(self.anti_burst_check)

        self.ttft_check = QCheckBox("开启首字延迟呼吸状态 (TTFT 等待提示)", group_algo)
        self.ttft_check.setToolTip("等待首字返回前显示呼吸态 [⏳ 响应中...]，拒绝显示误导性的 0.0 tok/s")
        algo_layout.addWidget(self.ttft_check)
        card_layout.addWidget(group_algo)

        card_layout.addStretch()

        # 6. Bottom action buttons
        btn_layout = QHBoxLayout()
        restore_btn = QPushButton("恢复默认设置", card)
        restore_btn.setObjectName("dangerBtn")
        restore_btn.clicked.connect(self._restore_defaults)
        btn_layout.addWidget(restore_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("取消", card)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存并应用", card)
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_and_apply)
        btn_layout.addWidget(save_btn)

        card_layout.addLayout(btn_layout)
        root_layout.addWidget(card)

    def _load_from_settings(self):
        """Populate form controls with current settings."""
        self.path_edit.setText(self.settings.db_path)
        self._check_db_status(self.settings.db_path)

        # Interval combo
        idx = self.interval_combo.findData(self.settings.refresh_interval_ms)
        if idx >= 0:
            self.interval_combo.setCurrentIndex(idx)

        # Mode combo
        mode_idx = self.mode_combo.findData(self.settings.start_mini)
        if mode_idx >= 0:
            self.mode_combo.setCurrentIndex(mode_idx)

        # Opacity slider
        val = int(self.settings.opacity * 100)
        self.opacity_slider.setValue(val)
        self.opacity_val_label.setText(f"{val}%")

        # Checkboxes
        self.topmost_check.setChecked(self.settings.always_on_top)
        self.lock_check.setChecked(self.settings.locked)
        self.anti_burst_check.setChecked(self.settings.enable_anti_burst)
        self.ttft_check.setChecked(self.settings.enable_ttft)

    def _check_db_status(self, path: str):
        """Check whether the database path exists and update status text."""
        p = path.strip()
        if os.path.exists(p):
            self.db_status_label.setText("✔ 数据库连接正常")
            self.db_status_label.setStyleSheet("color: #10B981; font-size: 11px;")
        else:
            self.db_status_label.setText("✕ 文件不存在，请检查路径")
            self.db_status_label.setStyleSheet("color: #EF4444; font-size: 11px;")

    def _browse_db_file(self):
        """Open native file dialog to locate opencode.db."""
        cur = self.path_edit.text().strip()
        start_dir = os.path.dirname(cur) if os.path.exists(cur) else os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 OpenCode 数据库文件",
            start_dir,
            "SQLite 数据库 (*.db *.sqlite);;所有文件 (*.*)"
        )
        if file_path:
            self.path_edit.setText(os.path.normpath(file_path))

    def _reset_default_db(self):
        """Reset path to default OpenCode SQLite path."""
        self.path_edit.setText(DEFAULT_DB_PATH)

    def _restore_defaults(self):
        """Reset all UI controls to factory default settings."""
        defaults = AppSettings()
        self.settings = defaults
        self._load_from_settings()

    def _save_and_apply(self):
        """Save settings to disk and invoke callback."""
        self.settings.db_path = self.path_edit.text().strip()
        self.settings.refresh_interval_ms = self.interval_combo.currentData()
        self.settings.start_mini = self.mode_combo.currentData()
        self.settings.opacity = self.opacity_slider.value() / 100.0
        self.settings.always_on_top = self.topmost_check.isChecked()
        self.settings.locked = self.lock_check.isChecked()
        self.settings.enable_anti_burst = self.anti_burst_check.isChecked()
        self.settings.enable_ttft = self.ttft_check.isChecked()

        # Save to disk
        self.settings.save()

        # Trigger callback in main window
        if self.on_apply_callback:
            self.on_apply_callback(self.settings)

        self.accept()
