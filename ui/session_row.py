# -*- coding: utf-8 -*-
"""
Single session monitoring UI row component.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont

from core.models import SessionMetrics, ForegroundInfo
from .styles import BADGE_STYLES


class SessionRowWidget(QFrame):
    """Single session status row widget."""

    def __init__(self, row_index: int, parent=None):
        super().__init__(parent)
        self.row_index = row_index
        self.init_ui()

    def init_ui(self):
        self.setObjectName(f"row_{self.row_index}")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # 1. Status badge (Foreground / Background / Subagent / Idle)
        self.badge_label = QLabel("待命", self)
        self.badge_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.set_badge_style("idle")
        layout.addWidget(self.badge_label, 0, Qt.AlignVCenter)

        # 2. Project or session directory name
        self.name_label = QLabel("---", self)
        self.name_label.setStyleSheet("color: #F3F4F6; font-size: 12px; font-weight: 600; font-family: 'Segoe UI', 'Microsoft YaHei UI', 'Microsoft YaHei';")
        self.name_label.setMaximumWidth(140)
        layout.addWidget(self.name_label)

        # 3. Dynamic throughput rate or generation status
        self.speed_label = QLabel("-- tok/s", self)
        self.speed_label.setStyleSheet("color: #00FFCC; font-size: 12px; font-weight: bold; font-family: 'Consolas', 'Segoe UI';")
        layout.addWidget(self.speed_label)

        layout.addStretch()

        # 4. Details (Elapsed | Tokens | Model)
        self.detail_label = QLabel("", self)
        self.detail_label.setStyleSheet("color: #9CA3AF; font-size: 11px; font-family: 'Segoe UI', 'Microsoft YaHei UI', 'Microsoft YaHei';")
        layout.addWidget(self.detail_label)

    def set_badge_style(self, badge_type: str):
        """Apply CSS styling to status badge."""
        badge_info = BADGE_STYLES.get(badge_type, BADGE_STYLES["idle"])
        self.badge_label.setStyleSheet(badge_info["style"])

    def update_data(self, badge_type: str, badge_text: str, name: str, speed_text: str, speed_color: str, detail_text: str, tooltip: str = ""):
        """Low-level primitive data rendering."""
        self.set_badge_style(badge_type)
        self.badge_label.setText(badge_text)

        # Truncate overly long names
        display_name = name if len(name) <= 16 else (name[:14] + "..")
        self.name_label.setText(display_name)

        self.speed_label.setText(speed_text)
        self.speed_label.setStyleSheet(f"color: {speed_color}; font-size: 12px; font-weight: bold; font-family: 'Consolas', 'Segoe UI';")
        self.detail_label.setText(detail_text)
        self.setToolTip(tooltip)

    def render_session(self, s: SessionMetrics, is_foreground_row: bool = False, is_focused: bool = True, fg_info: ForegroundInfo = None):
        """Format and update row widgets with domain metrics."""
        if is_foreground_row:
            if is_focused:
                badge_type = "fg"
                badge_text = "前台"
            else:
                badge_type = "fg_unfocused"
                badge_text = "前台·挂起"
        else:
            if s.parent_id:
                badge_type = "subagent"
                badge_text = "子任务"
            else:
                badge_type = "bg"
                badge_text = "后台"

        name = s.dir_name
        tps = s.tps
        decode_tps = s.decode_tps
        ttft_s = s.ttft_s
        decode_s = s.decode_s
        total_s = s.total_s
        total_out = s.total_out
        model = s.model.replace("deepseek-", "ds-")  # Abbreviate common model names for readability

        if s.is_waiting_ttft:
            # TTFT waiting phase: show breathing state instead of misleading 0.0 tok/s
            speed_text = "⏳ 响应中..."
            speed_color = "#FBBF24"  # Amber yellow
            detail_text = f"等待 {ttft_s:.1f}s | {model}"
        elif s.is_generating:
            # Streaming decoding phase: show pure decode generation throughput
            speed_text = f"⚡ {tps:.1f} tok/s"
            speed_color = "#00FFCC"  # Neon cyan-green
            detail_text = f"吐字 {decode_s:.1f}s (TTFT {ttft_s:.1f}s) | ~{int(total_out)}tok | {model}"
        elif s.is_burst:
            # Buffered burst delivery: fallback to human-perceived throughput with burst info
            speed_text = f"📦 {tps:.1f} tok/s"
            speed_color = "#38BDF8"  # Sky blue
            detail_text = f"整包 {total_s:.1f}s (突发 {decode_tps:.0f}t/s) | {total_out}tok | {model}"
        else:
            # Normal streaming completion state
            speed_text = f"✔ {tps:.1f} tok/s" if tps > 0 else "-- tok/s"
            speed_color = "#10B981" if tps > 0 else "#9CA3AF"  # Emerald green
            detail_text = f"{total_s:.1f}s (TTFT {ttft_s:.1f}s) | {total_out}tok | {model}"

        self.update_data(
            badge_type=badge_type,
            badge_text=badge_text,
            name=name,
            speed_text=speed_text,
            speed_color=speed_color,
            detail_text=detail_text,
            tooltip=s.tooltip
        )
