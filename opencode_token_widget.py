# -*- coding: utf-8 -*-
"""
OpenCode Real-time Token Speed and Usage Monitor (Backward Compatibility Entry Point).

Note: This project has been modularized and decoupled:
- Core telemetry and anti-burst rate algorithms: located in `core/` (supports headless CLI execution)
- Desktop floating widget and tray interaction: located in `ui/`
- Primary application entry point: `main.py`

This file is maintained for 100% backward compatibility with legacy scripts and packaging flows.
"""

import sys
import os

# Import decoupled core modules and maintain backward compatibility
from core import (
    DEFAULT_DB_PATH,
    DEFAULT_REFRESH_INTERVAL_MS,
    WindowHelper,
    ForegroundInfo,
    SessionMetrics,
    MonitorState,
    OpenCodeTelemetry,
    get_resource_path,
)
from ui import (
    CARD_STYLE,
    MENU_STYLE,
    BADGE_STYLES,
    SessionRowWidget,
    TrayManager,
    OpenCodeTokenMonitor,
)
from main import main

# Compatibility alias
DB_PATH = DEFAULT_DB_PATH

if __name__ == "__main__":
    main()
