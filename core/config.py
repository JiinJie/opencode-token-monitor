# -*- coding: utf-8 -*-
"""
Core configuration, global constants, metadata, and persistent settings manager.
"""

import os
import sys
import json
from typing import Optional
from dataclasses import dataclass, asdict

# Application metadata
APP_NAME = "OpenCode Token Monitor"
APP_VERSION = "v1.1.0"
APP_DESCRIPTION = "专为 OpenCode 打造的轻量级实时 Token 速率与用量悬浮监控器"
AUTHOR_NAME = "JiinJie"
AUTHOR_GITHUB = "https://github.com/JiinJie"
PROJECT_GITHUB = "https://github.com/JiinJie/opencode-token-monitor"

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


# Storage location modes
STORAGE_MODE_PORTABLE = "portable"  # Current execution directory (portable mode)
STORAGE_MODE_APPDATA = "app_data"   # Standard system user directory (%APPDATA%/OpenCodeTokenMonitor)


def get_app_dir() -> str:
    """Get the directory of the running application / script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_appdata_dir() -> str:
    """Get standard user configuration directory (%APPDATA%/OpenCodeTokenMonitor)."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "OpenCodeTokenMonitor")


def get_storage_dir(mode: str = STORAGE_MODE_PORTABLE) -> str:
    """Get base directory for config and logs based on storage mode."""
    if mode == STORAGE_MODE_APPDATA:
        d = get_appdata_dir()
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        return d
    return get_app_dir()


def get_settings_file_path(mode: str = None) -> str:
    """
    Get the path to settings.json.
    If mode is specified ('portable' or 'app_data'), return that specific path.
    Otherwise, auto-detect by inspecting app_dir and appdata_dir.
    """
    if mode:
        return os.path.join(get_storage_dir(mode), "settings.json")

    # 1. Check local app_dir
    local_cfg = os.path.join(get_app_dir(), "settings.json")
    if os.path.exists(local_cfg):
        try:
            with open(local_cfg, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("storage_mode") == STORAGE_MODE_APPDATA:
                    appdata_cfg = os.path.join(get_appdata_dir(), "settings.json")
                    if os.path.exists(appdata_cfg):
                        return appdata_cfg
                return local_cfg
        except Exception:
            return local_cfg

    # 2. Check appdata
    appdata_cfg = os.path.join(get_appdata_dir(), "settings.json")
    if os.path.exists(appdata_cfg):
        return appdata_cfg

    # 3. Default fallback: local app_dir
    return local_cfg


def get_log_file_path(mode: str = None) -> str:
    """Get the path to widget.log based on storage mode."""
    if not mode:
        cfg_path = get_settings_file_path()
        if get_appdata_dir().lower() in os.path.abspath(cfg_path).lower():
            mode = STORAGE_MODE_APPDATA
        else:
            mode = STORAGE_MODE_PORTABLE
    return os.path.join(get_storage_dir(mode), "widget.log")


@dataclass
class AppSettings:
    """Application persistent user configuration model."""
    db_path: str = DEFAULT_DB_PATH
    refresh_interval_ms: int = DEFAULT_REFRESH_INTERVAL_MS
    display_rows: int = 3  # Configurable range: 1 - 8 rows
    enable_anti_burst: bool = True
    enable_ttft: bool = True
    start_mini: bool = False
    locked: bool = False
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    opacity: float = 1.0  # Range: 0.5 - 1.0 (50% to 100%)
    storage_mode: str = STORAGE_MODE_PORTABLE  # 'portable' or 'app_data'

    @classmethod
    def load(cls) -> "AppSettings":
        """Load settings from JSON file or fall back to defaults."""
        path = get_settings_file_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    valid_keys = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
                    inst = cls(**valid_keys)
                    if not (1 <= inst.display_rows <= 8):
                        inst.display_rows = 3
                    if not (0.3 <= inst.opacity <= 1.0):
                        inst.opacity = 1.0
                    if inst.storage_mode not in (STORAGE_MODE_PORTABLE, STORAGE_MODE_APPDATA):
                        inst.storage_mode = STORAGE_MODE_PORTABLE
                    return inst
            except Exception:
                pass
        return cls()

    def save(self, target_mode: str = None) -> bool:
        """Persist current settings to JSON file according to storage_mode."""
        mode = target_mode or self.storage_mode
        self.storage_mode = mode
        path = get_settings_file_path(mode=mode)
        try:
            target_dir = os.path.dirname(path)
            os.makedirs(target_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)

            # If saving to app_data, write redirect pointer into app_dir
            local_path = os.path.join(get_app_dir(), "settings.json")
            if mode == STORAGE_MODE_APPDATA and os.path.abspath(path) != os.path.abspath(local_path):
                try:
                    with open(local_path, "w", encoding="utf-8") as f:
                        json.dump({"storage_mode": STORAGE_MODE_APPDATA}, f, indent=2)
                except Exception:
                    pass
            elif mode == STORAGE_MODE_PORTABLE:
                # If saving to portable, clean up redirect in appdata if it was just a pointer
                appdata_path = os.path.join(get_appdata_dir(), "settings.json")
                if os.path.exists(appdata_path) and os.path.abspath(path) != os.path.abspath(appdata_path):
                    try:
                        with open(appdata_path, "w", encoding="utf-8") as f:
                            json.dump({"storage_mode": STORAGE_MODE_PORTABLE}, f, indent=2)
                    except Exception:
                        pass
            return True
        except Exception:
            return False
