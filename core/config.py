# -*- coding: utf-8 -*-
"""
Core configuration and global constants.
"""

import os
import sys

# Default OpenCode SQLite telemetry database path
DEFAULT_DB_PATH = os.environ.get("OPENCODE_DB_PATH") or os.path.expanduser(
    r"~\.local\share\opencode\opencode.db"
)

# Default refresh interval parameters
DEFAULT_REFRESH_INTERVAL_MS = 500
SUPPORTED_REFRESH_INTERVALS = [
    (250, "高频 (250ms)"),
    (500, "标准 (500ms)"),
    (1000, "节能 (1000ms)"),
]

# Anti-Burst Detection Thresholds
BURST_DECODE_THRESHOLD_S = 0.6       # Upper bound for suspiciously short decode duration (seconds)
BURST_MIN_TOKENS = 25                # Minimum tokens to trigger anti-burst logic
BURST_RATIO_THRESHOLD = 0.15         # Lower bound for decode duration ratio against total time
BURST_MIN_TOTAL_S = 2.0              # Minimum total elapsed time (seconds)


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    Compatible with source runs, modular package structure, and PyInstaller bundled environments.
    """
    # 1. Check PyInstaller temporary unpacked directory (_MEIPASS)
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            p = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(p):
                return p
        exe_dir = os.path.dirname(sys.executable)
        p = os.path.join(exe_dir, relative_path)
        if os.path.exists(p):
            return p

    # 2. Check assets/ directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p_assets = os.path.join(base_dir, "assets", relative_path)
    if os.path.exists(p_assets):
        return p_assets

    # 3. Check project root directory
    p_root = os.path.join(base_dir, relative_path)
    if os.path.exists(p_root):
        return p_root

    return relative_path
