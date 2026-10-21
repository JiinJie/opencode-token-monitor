# -*- coding: utf-8 -*-
"""
Application preferences and settings management dialog with smooth scrolling.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QGroupBox, QSlider,
    QRadioButton, QButtonGroup, QApplication,
    QFileDialog, QFrame, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont

from core.config import (
    APP_NAME, DEFAULT_DB_PATH, DEFAULT_REFRESH_INTERVAL_MS,
    SUPPORTED_REFRESH_INTERVALS, AppSettings,
    STORAGE_MODE_PORTABLE, STORAGE_MODE_APPDATA,
    get_app_dir, get_appdata_dir, get_storage_dir,
    get_settings_file_path, get_log_file_path
)
from .styles import DIALOG_STYLE


class SettingsDialog(QDialog):
    """Modern dark-themed preferences dialog with scrollable content."""

    def __init__(self, current_settings: AppSettings, on_apply_callback=None, on_reset_position_callback=None, parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.on_apply_callback = on_apply_callback
        self.on_reset_position_callback = on_reset_position_callback
        self.orig_opacity = current_settings.opacity

        self.setWindowTitle(f"设置 - {APP_NAME}")
        self.resize(560, 560)
        self.setMinimumSize(500, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFont(QFont("Microsoft YaHei UI", 9))
        self.setStyleSheet(DIALOG_STYLE)

        # Disable Qt slow sliding animation on combobox dropdowns for instant popup
        QApplication.setEffectEnabled(Qt.UI_AnimateCombo, False)

        self._init_ui()
        self._load_from_settings()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(0)

        card = QFrame(self)
        card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        # 1. Top Fixed Header
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title_label = QLabel("⚙️ 监控与偏好设置", card)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        header_box.addWidget(title_label)

        sub_label = QLabel("自定义 OpenCode 数据库路径、采样频率与防虚标算法参数", card)
        sub_label.setStyleSheet("font-size: 11px; color: #94A3B8;")
        header_box.addWidget(sub_label)
        card_layout.addLayout(header_box)

        # Divider
        div_top = QFrame(card)
        div_top.setFrameShape(QFrame.HLine)
        div_top.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(div_top)

        # 2. Middle Scrollable Area
        scroll_area = QScrollArea(card)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea, QScrollArea > QWidget > QWidget {
                background-color: transparent;
                border: none;
            }
            QWidget#scrollContent {
                background-color: transparent;
            }
        """)
        scroll_area.viewport().setStyleSheet("background-color: transparent;")

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(4, 4, 12, 10)
        scroll_layout.setSpacing(16)

        # --- Group 1: Data Source (Database Path) ---
        group_db = QGroupBox("📂 遥测数据源 (OpenCode 数据库)", scroll_content)
        db_layout = QVBoxLayout(group_db)
        db_layout.setSpacing(8)
        db_layout.setContentsMargins(12, 18, 12, 14)

        db_hint = QLabel("监控器通过只读模式监听该数据库，获取流式吐字与会话遥测数据：", group_db)
        db_hint.setStyleSheet("color: #94A3B8; font-size: 11px;")
        db_hint.setWordWrap(True)
        db_layout.addWidget(db_hint)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_edit = QLineEdit(group_db)
        self.path_edit.setMinimumHeight(32)
        self.path_edit.setPlaceholderText("请输入或选择 opencode.db 路径...")
        self.path_edit.textChanged.connect(self._check_db_status)
        path_row.addWidget(self.path_edit)

        browse_btn = QPushButton("浏览", group_db)
        browse_btn.setFixedWidth(72)
        browse_btn.setMinimumHeight(32)
        browse_btn.clicked.connect(self._browse_db_file)
        path_row.addWidget(browse_btn)

        reset_btn = QPushButton("默认", group_db)
        reset_btn.setFixedWidth(56)
        reset_btn.setMinimumHeight(32)
        reset_btn.setToolTip("恢复为系统默认数据库路径")
        reset_btn.clicked.connect(self._reset_default_db)
        path_row.addWidget(reset_btn)
        db_layout.addLayout(path_row)

        self.db_status_label = QLabel("", group_db)
        self.db_status_label.setStyleSheet("font-size: 11px;")
        db_layout.addWidget(self.db_status_label)

        scroll_layout.addWidget(group_db)

        # --- Group 2: Performance & Sampling Interval ---
        group_perf = QGroupBox("⚡ 性能与采样频率", scroll_content)
        perf_layout = QVBoxLayout(group_perf)
        perf_layout.setSpacing(8)
        perf_layout.setContentsMargins(12, 18, 12, 14)

        row_int = QHBoxLayout()
        row_int.addWidget(QLabel("采样刷新间隔:", group_perf))
        self.interval_combo = QComboBox(group_perf)
        self.interval_combo.setMinimumHeight(28)
        for ms, label in SUPPORTED_REFRESH_INTERVALS:
            self.interval_combo.addItem(label, ms)
        row_int.addWidget(self.interval_combo)
        row_int.addStretch()
        perf_layout.addLayout(row_int)

        perf_hint = QLabel("• 250ms (高频)：更快感知吐字波动；\n• 500ms (标准)：平稳流畅推荐；\n• 1000ms (节能)：系统占用极低。", group_perf)
        perf_hint.setStyleSheet("color: #64748B; font-size: 11px; line-height: 140%;")
        perf_layout.addWidget(perf_hint)

        scroll_layout.addWidget(group_perf)

        # --- Group 3: Detection Algorithm ---
        group_algo = QGroupBox("🛡️ 速率与延迟算法", scroll_content)
        algo_layout = QVBoxLayout(group_algo)
        algo_layout.setSpacing(10)
        algo_layout.setContentsMargins(12, 18, 12, 14)

        self.anti_burst_check = QCheckBox("开启防整包突发虚标校准 (Anti-Burst Detection)", group_algo)
        self.anti_burst_check.setStyleSheet("color: #F3F4F6; font-size: 12px; font-weight: 500;")
        algo_layout.addWidget(self.anti_burst_check)

        anti_burst_tip = QLabel("当反向代理服务端中途缓冲后一口气整包推送时，自动以真实端到端体感速率校准，杜绝虚假上千 Token/s。", group_algo)
        anti_burst_tip.setStyleSheet("color: #94A3B8; font-size: 11px; margin-left: 24px;")
        anti_burst_tip.setWordWrap(True)
        algo_layout.addWidget(anti_burst_tip)

        self.ttft_check = QCheckBox("开启首字延迟呼吸状态 (TTFT 阶段感知)", group_algo)
        self.ttft_check.setStyleSheet("color: #F3F4F6; font-size: 12px; font-weight: 500;")
        algo_layout.addWidget(self.ttft_check)

        ttft_tip = QLabel("首字返回前显示呼吸动态 [⏳ 响应中...]，明确展示排队与思考耗时，避免显示误导性的 0.0 tok/s。", group_algo)
        ttft_tip.setStyleSheet("color: #94A3B8; font-size: 11px; margin-left: 24px;")
        ttft_tip.setWordWrap(True)
        algo_layout.addWidget(ttft_tip)

        scroll_layout.addWidget(group_algo)

        # --- Group 4: Window & Display Preferences ---
        group_win = QGroupBox("📌 列表显示与启动偏好", scroll_content)
        win_layout = QVBoxLayout(group_win)
        win_layout.setSpacing(10)
        win_layout.setContentsMargins(12, 18, 12, 14)

        # Row: Display Rows Count (1 - 8)
        row_count_layout = QHBoxLayout()
        row_count_label = QLabel("列表展示会话行数:", group_win)
        row_count_label.setStyleSheet("color: #F3F4F6; font-size: 12px;")
        row_count_layout.addWidget(row_count_label)

        self.rows_combo = QComboBox(group_win)
        self.rows_combo.setMinimumHeight(28)
        for n in range(1, 9):
            text = f"{n} 行 (默认推荐)" if n == 3 else f"{n} 行"
            self.rows_combo.addItem(text, n)
        row_count_layout.addWidget(self.rows_combo)
        row_count_layout.addStretch()
        win_layout.addLayout(row_count_layout)

        rows_tip = QLabel("主面板支持展示 1 至 8 行会话（第 1 行为前台当前任务，其余行为后台活动会话或 Subagent）。", group_win)
        rows_tip.setStyleSheet("color: #64748B; font-size: 11px;")
        rows_tip.setWordWrap(True)
        win_layout.addWidget(rows_tip)

        # Row: Window Opacity (30% - 100%)
        row_opacity_layout = QHBoxLayout()
        row_opacity_label = QLabel("悬浮窗不透明度:", group_win)
        row_opacity_label.setStyleSheet("color: #F3F4F6; font-size: 12px;")
        row_opacity_layout.addWidget(row_opacity_label)

        self.opacity_slider = QSlider(Qt.Horizontal, group_win)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setSingleStep(5)
        self.opacity_slider.setFixedWidth(150)
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        row_opacity_layout.addWidget(self.opacity_slider)

        self.opacity_val_label = QLabel("100%", group_win)
        self.opacity_val_label.setFixedWidth(42)
        self.opacity_val_label.setStyleSheet("color: #00FFCC; font-size: 12px; font-weight: bold; font-family: 'Consolas', 'Segoe UI';")
        row_opacity_layout.addWidget(self.opacity_val_label)
        row_opacity_layout.addStretch()
        win_layout.addLayout(row_opacity_layout)

        self.start_mini_check = QCheckBox("启动时默认进入 1 行极简迷你胶囊模式", group_win)
        self.start_mini_check.setStyleSheet("color: #F3F4F6; font-size: 12px;")
        win_layout.addWidget(self.start_mini_check)

        self.lock_check = QCheckBox("锁定悬浮窗位置 (防止鼠标误触拖拽移动)", group_win)
        self.lock_check.setStyleSheet("color: #F3F4F6; font-size: 12px;")
        win_layout.addWidget(self.lock_check)

        # Row: Reset Window Position
        row_pos_layout = QHBoxLayout()
        row_pos_label = QLabel("停靠位置异常或溢出屏幕:", group_win)
        row_pos_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        row_pos_layout.addWidget(row_pos_label)

        reset_pos_btn = QPushButton("复位窗口至右上角", group_win)
        reset_pos_btn.setMinimumHeight(26)
        reset_pos_btn.setToolTip("立即将悬浮窗复位恢复到主屏幕右上角")
        reset_pos_btn.clicked.connect(self._reset_window_position)
        row_pos_layout.addWidget(reset_pos_btn)
        row_pos_layout.addStretch()
        win_layout.addLayout(row_pos_layout)

        scroll_layout.addWidget(group_win)

        # --- Group 5: Configuration & Log Storage Location ---
        group_storage = QGroupBox("📁 配置文件与运行日志位置", scroll_content)
        storage_layout = QVBoxLayout(group_storage)
        storage_layout.setSpacing(10)
        storage_layout.setContentsMargins(12, 18, 12, 14)

        storage_tip = QLabel("可自由选择配置文件 (settings.json) 与运行日志 (opencode_monitor.log) 的持久化保存位置：", group_storage)
        storage_tip.setStyleSheet("color: #94A3B8; font-size: 11px;")
        storage_tip.setWordWrap(True)
        storage_layout.addWidget(storage_tip)

        self.storage_btn_group = QButtonGroup(group_storage)

        # Option 1: Portable Mode (app directory)
        self.radio_portable = QRadioButton("当前执行文件所在文件夹 (绿色便携模式 Portable)", group_storage)
        self.radio_portable.setStyleSheet("color: #F3F4F6; font-size: 12px; font-weight: 500;")
        self.storage_btn_group.addButton(self.radio_portable, 1)
        storage_layout.addWidget(self.radio_portable)

        portable_hint = QLabel(f"• 路径: {get_app_dir()}\n  配置与日志直接跟随程序脚本/可执行文件，适合免安装便携移动使用。", group_storage)
        portable_hint.setStyleSheet("color: #64748B; font-size: 11px; margin-left: 24px;")
        portable_hint.setWordWrap(True)
        storage_layout.addWidget(portable_hint)

        # Option 2: Standard User AppData
        self.radio_appdata = QRadioButton("系统用户默认数据位置 (标准模式 AppData)", group_storage)
        self.radio_appdata.setStyleSheet("color: #F3F4F6; font-size: 12px; font-weight: 500;")
        self.storage_btn_group.addButton(self.radio_appdata, 2)
        storage_layout.addWidget(self.radio_appdata)

        appdata_hint = QLabel(f"• 路径: {get_appdata_dir()}\n  遵循标准 Windows 应用程序规范，不产生本地写入污染，适合日常长期使用。", group_storage)
        appdata_hint.setStyleSheet("color: #64748B; font-size: 11px; margin-left: 24px;")
        appdata_hint.setWordWrap(True)
        storage_layout.addWidget(appdata_hint)

        # Action: Open Storage Folder
        storage_action_row = QHBoxLayout()
        self.open_folder_btn = QPushButton("📂 打开当前存储文件夹", group_storage)
        self.open_folder_btn.setMinimumHeight(28)
        self.open_folder_btn.setToolTip("在 Windows 资源管理器中打开当前选中的配置与日志存储目录")
        self.open_folder_btn.clicked.connect(self._open_storage_folder)
        storage_action_row.addWidget(self.open_folder_btn)
        storage_action_row.addStretch()
        storage_layout.addLayout(storage_action_row)

        scroll_layout.addWidget(group_storage)

        scroll_area.setWidget(scroll_content)
        card_layout.addWidget(scroll_area)

        # Divider
        div_bottom = QFrame(card)
        div_bottom.setFrameShape(QFrame.HLine)
        div_bottom.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(div_bottom)

        # 3. Bottom Action Bar (Fixed, never squeezed)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 0)

        restore_btn = QPushButton("恢复默认", card)
        restore_btn.setObjectName("dangerBtn")
        restore_btn.setMinimumHeight(32)
        restore_btn.clicked.connect(self._restore_defaults)
        btn_layout.addWidget(restore_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("取消", card)
        cancel_btn.setMinimumHeight(32)
        cancel_btn.setFixedWidth(75)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存并应用", card)
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(32)
        save_btn.setFixedWidth(95)
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

        # Display rows combo
        rows_idx = self.rows_combo.findData(self.settings.display_rows)
        if rows_idx >= 0:
            self.rows_combo.setCurrentIndex(rows_idx)
        else:
            self.rows_combo.setCurrentIndex(2)  # Default: 3 rows

        # Opacity slider
        op_pct = int(round(self.settings.opacity * 100))
        self.opacity_slider.setValue(max(30, min(100, op_pct)))
        self.opacity_val_label.setText(f"{self.opacity_slider.value()}%")

        # Checkboxes
        self.anti_burst_check.setChecked(self.settings.enable_anti_burst)
        self.ttft_check.setChecked(self.settings.enable_ttft)
        self.start_mini_check.setChecked(self.settings.start_mini)
        self.lock_check.setChecked(self.settings.locked)

        # Storage mode
        if self.settings.storage_mode == STORAGE_MODE_APPDATA:
            self.radio_appdata.setChecked(True)
        else:
            self.radio_portable.setChecked(True)

    def _open_storage_folder(self):
        """Open currently selected storage folder in Windows Explorer."""
        selected_mode = STORAGE_MODE_APPDATA if self.radio_appdata.isChecked() else STORAGE_MODE_PORTABLE
        target_dir = get_storage_dir(selected_mode)
        try:
            os.makedirs(target_dir, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(target_dir))
        except Exception:
            pass

    def _on_opacity_slider_changed(self, val: int):
        """Update opacity label and live-preview transparency on floating window."""
        self.opacity_val_label.setText(f"{val}%")
        if self.parent():
            try:
                self.parent().setWindowOpacity(val / 100.0)
            except Exception:
                pass

    def _reset_window_position(self):
        """Invoke position reset callback to snap widget back to primary screen top-right."""
        if self.on_reset_position_callback:
            self.on_reset_position_callback()
            self.db_status_label.setText("✔ 悬浮窗已成功复位至主屏幕右上角")
            self.db_status_label.setStyleSheet("color: #10B981; font-size: 11px;")

    def _check_db_status(self, path: str):
        """Check whether the database path exists and update status indicator."""
        p = path.strip()
        if os.path.exists(p):
            self.db_status_label.setText("✔ 数据库文件正常 (已连接)")
            self.db_status_label.setStyleSheet("color: #10B981; font-size: 11px;")
        else:
            self.db_status_label.setText("✕ 文件不存在，请确认路径是否正确")
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
        self.settings = AppSettings()
        self._load_from_settings()
        if self.parent():
            try:
                self.parent().setWindowOpacity(1.0)
            except Exception:
                pass

    def reject(self):
        """Restore original opacity if user cancelled without saving."""
        if self.parent():
            try:
                self.parent().setWindowOpacity(self.orig_opacity)
            except Exception:
                pass
        super().reject()

    def _save_and_apply(self):
        """Save settings to disk and invoke callback."""
        self.settings.db_path = self.path_edit.text().strip()
        self.settings.refresh_interval_ms = self.interval_combo.currentData()
        self.settings.display_rows = self.rows_combo.currentData() or 3
        self.settings.opacity = self.opacity_slider.value() / 100.0
        self.settings.enable_anti_burst = self.anti_burst_check.isChecked()
        self.settings.enable_ttft = self.ttft_check.isChecked()
        self.settings.start_mini = self.start_mini_check.isChecked()
        self.settings.locked = self.lock_check.isChecked()
        new_storage_mode = STORAGE_MODE_APPDATA if self.radio_appdata.isChecked() else STORAGE_MODE_PORTABLE
        self.settings.storage_mode = new_storage_mode

        # Save to disk in designated storage mode
        self.settings.save(target_mode=new_storage_mode)

        # Trigger callback in main window
        if self.on_apply_callback:
            self.on_apply_callback(self.settings)

        self.accept()
