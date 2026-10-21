# -*- coding: utf-8 -*-
"""
OpenCode Real-time Token & Throughput Desktop Monitor Launcher.
Supports both PyQt5 GUI desktop floating widget mode and pure CLI console mode.
"""

import sys
import os
import time
import argparse

# Ensure project root directory is present in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.config import (
    DEFAULT_DB_PATH, DEFAULT_REFRESH_INTERVAL_MS,
    AppSettings
)
from core.telemetry import OpenCodeTelemetry


def run_cli_mode(db_path: str = None, interval_ms: int = None):
    """Pure CLI terminal monitor mode (requires no graphical display)."""
    settings = AppSettings.load()
    target_db = db_path or settings.db_path
    target_interval = interval_ms or settings.refresh_interval_ms

    telemetry = OpenCodeTelemetry(
        db_path=target_db,
        enable_anti_burst=settings.enable_anti_burst,
        enable_ttft=settings.enable_ttft
    )
    interval_s = max(0.2, target_interval / 1000.0)

    print("=" * 65)
    print("  OpenCode Token Monitor (CLI Mode)")
    print(f"  Telemetry Database: {target_db}")
    print(f"  Polling Interval: {target_interval} ms | Press Ctrl+C to exit")
    print("=" * 65)

    try:
        while True:
            state = telemetry.collect()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"[{time.strftime('%H:%M:%S')}] OpenCode Telemetry Monitor")
            print("-" * 65)

            if not state.db_exists:
                print("  [Notice] OpenCode database not found. Please verify the database path.")
            elif not state.foreground_session:
                print("  [Notice] No active session records found in database.")
            else:
                fg = state.foreground_session
                fg_tag = "FG (Focus)" if state.is_opencode_foreground else "FG (Suspended)"
                burst_tag = " [Burst Protected]" if fg.is_burst else ""
                print(f"  [{fg_tag}] {fg.dir_name:<16} | ⚡ {fg.tps:>6.1f} tok/s{burst_tag} | {fg.model}")
                print(f"          Duration: {fg.total_s:.1f}s (TTFT {fg.ttft_s:.1f}s) | Output: {fg.total_out} tok")

                for i, s in enumerate(state.other_sessions[:2]):
                    b_tag = "Subtask" if s.parent_id else "BG"
                    print(f"  [{b_tag:<7}] {s.dir_name:<16} | ⚡ {s.tps:>6.1f} tok/s | {s.model}")

            print("-" * 65)
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("\nExited CLI monitor mode.")


def run_gui_mode(db_path: str, interval_ms: int, start_mini: bool = False):
    """Launch PyQt5 desktop floating widget mode."""
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import OpenCodeTokenMonitor

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = BASE_DIR
    log_path = os.path.join(app_dir, "widget.log")

    try:
        app = QApplication(sys.argv)
        # Keep application running in system tray when window is hidden
        app.setQuitOnLastWindowClosed(False)

        monitor = OpenCodeTokenMonitor(db_path=db_path, refresh_interval=interval_ms)
        if start_mini:
            monitor.toggle_mini_mode()
        monitor.show()

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Widget started successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(traceback.format_exc())


def main():
    parser = argparse.ArgumentParser(description="OpenCode Real-time Token Speed and Usage Desktop Floating Monitor")
    parser.add_argument("--db-path", default=None, help="Specify path to OpenCode SQLite telemetry database (default: from settings or ~/.local/share/opencode/opencode.db)")
    parser.add_argument("--interval", type=int, default=None, help="Refresh polling interval in milliseconds (default: from settings or 500ms)")
    parser.add_argument("--cli", action="store_true", help="Run in terminal CLI mode without starting GUI")
    parser.add_argument("--mini", action="store_true", help="Start minimized in 1-row mini capsule mode")

    args = parser.parse_args()

    if args.cli:
        run_cli_mode(db_path=args.db_path, interval_ms=args.interval)
    else:
        run_gui_mode(db_path=args.db_path, interval_ms=args.interval, start_mini=args.mini)


if __name__ == "__main__":
    main()
