# -*- coding: utf-8 -*-
"""
About dialog displaying application metadata, version, and author details.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

from core.config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    AUTHOR_NAME, AUTHOR_GITHUB, PROJECT_GITHUB,
    get_resource_path
)
from .styles import DIALOG_STYLE


class AboutDialog(QDialog):
    """Modern dark-themed application metadata and about modal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"关于 - {APP_NAME}")
        self.setFixedSize(420, 365)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFont(QFont("Microsoft YaHei UI", 9))
        self.setStyleSheet(DIALOG_STYLE)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)

        card = QFrame(self)
        card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 18)
        card_layout.setSpacing(12)

        # 1. Centered Hero Header (Icon + Title + Version Badge + Description)
        hero_box = QVBoxLayout()
        hero_box.setSpacing(6)
        hero_box.setAlignment(Qt.AlignCenter)

        # App Icon
        icon_label = QLabel(card)
        icon_path = get_resource_path("app_icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("⚡")
            icon_label.setStyleSheet("font-size: 32px; color: #00FFCC;")
        icon_label.setAlignment(Qt.AlignCenter)
        hero_box.addWidget(icon_label)

        # Centered App Title
        title_label = QLabel(APP_NAME, card)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        title_label.setAlignment(Qt.AlignCenter)
        hero_box.addWidget(title_label)

        # Centered Version Badge
        badge_box = QHBoxLayout()
        badge_box.addStretch()
        ver_badge = QLabel(f" {APP_VERSION} ", card)
        ver_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.22);
            color: #10B981;
            border: 1px solid #10B981;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 8px;
        """)
        badge_box.addWidget(ver_badge)
        badge_box.addStretch()
        hero_box.addLayout(badge_box)

        # Subtitle
        desc_label = QLabel(APP_DESCRIPTION, card)
        desc_label.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 2px;")
        desc_label.setAlignment(Qt.AlignCenter)
        hero_box.addWidget(desc_label)

        card_layout.addLayout(hero_box)

        # 2. Divider
        div = QFrame(card)
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(div)

        # 3. Clean Key-Value Grid Card
        info_frame = QFrame(card)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #171A22;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        grid = QGridLayout(info_frame)
        grid.setContentsMargins(18, 12, 18, 12)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        lbl_author = QLabel("👤 开发作者:", info_frame)
        lbl_author.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        val_author = QLabel(f"<a href='{AUTHOR_GITHUB}' style='color: #38BDF8; text-decoration: none;'>{AUTHOR_NAME} (GitHub ↗)</a>", info_frame)
        val_author.setOpenExternalLinks(True)
        grid.addWidget(lbl_author, 0, 0)
        grid.addWidget(val_author, 0, 1)

        lbl_repo = QLabel("🔗 开源仓库:", info_frame)
        lbl_repo.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        val_repo = QLabel(f"<a href='{PROJECT_GITHUB}' style='color: #00FFCC; text-decoration: none;'>JiinJie/opencode-token-monitor ↗</a>", info_frame)
        val_repo.setOpenExternalLinks(True)
        grid.addWidget(lbl_repo, 1, 0)
        grid.addWidget(val_repo, 1, 1)

        lbl_lic = QLabel("📄 开源协议:", info_frame)
        lbl_lic.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        val_lic = QLabel("MIT License", info_frame)
        val_lic.setStyleSheet("color: #E2E8F0; font-size: 12px;")
        grid.addWidget(lbl_lic, 2, 0)
        grid.addWidget(val_lic, 2, 1)

        card_layout.addWidget(info_frame)

        # 4. Bottom Centered Action Button
        card_layout.addStretch()
        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignCenter)
        close_btn = QPushButton("确定", card)
        close_btn.setObjectName("primaryBtn")
        close_btn.setMinimumHeight(32)
        close_btn.setFixedWidth(110)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        card_layout.addLayout(btn_box)

        root_layout.addWidget(card)
