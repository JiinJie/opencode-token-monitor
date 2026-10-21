# -*- coding: utf-8 -*-
"""
About dialog displaying application metadata, version, and author details.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices

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
        self.setFixedSize(400, 290)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)

        card = QFrame(self)
        card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        # Header with app icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel(card)
        icon_path = get_resource_path("app_icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("⚡")
            icon_label.setStyleSheet("font-size: 28px; color: #00FFCC;")
        header_layout.addWidget(icon_label)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(3)

        title_row = QHBoxLayout()
        title_label = QLabel(APP_NAME, card)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        title_row.addWidget(title_label)

        ver_badge = QLabel(f" {APP_VERSION} ", card)
        ver_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.25);
            color: #10B981;
            border: 1px solid #10B981;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            padding: 1px 4px;
        """)
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        title_vbox.addLayout(title_row)

        desc_label = QLabel(APP_DESCRIPTION, card)
        desc_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        desc_label.setWordWrap(True)
        title_vbox.addWidget(desc_label)

        header_layout.addLayout(title_vbox)
        card_layout.addLayout(header_layout)

        # Divider
        div = QFrame(card)
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(div)

        # Info links section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        author_label = QLabel(
            f"👤 作者: <a href='{AUTHOR_GITHUB}' style='color: #38BDF8; text-decoration: none;'>{AUTHOR_NAME} (GitHub)</a>",
            card
        )
        author_label.setOpenExternalLinks(True)
        author_label.setStyleSheet("font-size: 12px; color: #CBD5E1;")
        info_layout.addWidget(author_label)

        repo_label = QLabel(
            f"🔗 开源仓库: <a href='{PROJECT_GITHUB}' style='color: #00FFCC; text-decoration: none;'>JiinJie/opencode-token-monitor</a>",
            card
        )
        repo_label.setOpenExternalLinks(True)
        repo_label.setStyleSheet("font-size: 12px; color: #CBD5E1;")
        info_layout.addWidget(repo_label)

        license_label = QLabel("📄 开源协议: MIT License", card)
        license_label.setStyleSheet("font-size: 12px; color: #64748B;")
        info_layout.addWidget(license_label)

        card_layout.addLayout(info_layout)

        card_layout.addStretch()

        # Bottom close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("确定", card)
        close_btn.setObjectName("primaryBtn")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        card_layout.addLayout(btn_layout)
        root_layout.addWidget(card)
