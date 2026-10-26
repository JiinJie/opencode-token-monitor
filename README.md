# OpenCode Token Monitor

**English** | [简体中文](README_zh.md) | [日本語](README_ja.md) | [한국어](README_ko.md)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Overhead](https://img.shields.io/badge/Overhead-CPU%20%3C%200.2%25-brightgreen.svg)]()

A lightweight, zero-intrusion, multi-window aware desktop floating monitor specifically designed for **OpenCode**. Real-time tracking of foreground project and background session Token/s throughput, Time to First Token (TTFT), thinking/reasoning token consumption, and detailed request telemetry.

---

## 🌟 Key Features

- **🖥️ Smart Multi-Window & Multi-Session Awareness (Default 3 Rows)**:
  - **Row 1 [Active Foreground Window]**: Leverages native Windows APIs to automatically track the currently focused OpenCode window and workspace. When switching to other applications, it automatically flags the session as `[Foreground·Suspended]` while continuously capturing primary task throughput.
  - **Rows 2 & 3 [Recent Active Windows]**: Real-time display of recently active background sessions or subagent tasks.
- **🛡️ Proprietary Anti-Burst True Rate Algorithm**:
  - **TTFT Response Waiting Stage**: While waiting for the first token after sending a prompt (queuing, gateway handshake, prefill), displays an animated breathing indicator `⏳ Responding...` instead of a misleading `0.0 tok/s`.
  - **Smooth Streaming Stage (Decoding)**: Accurately isolates generation time by subtracting TTFT, presenting genuine model token output speed (`⚡ 194.9 tok/s`).
  - **Burst Buffer Anti-Spoof Protection**: Detects intermediate gateway or reverse-proxy buffering where tokens are released all at once. Automatically switches to end-to-end human-perceived throughput (`📦 50.0 tok/s [Burst]`), eliminating unrealistic multi-thousand tok/s spikes.
- **📌 Polished Capsule Widget Interaction**:
  - Translucent dark glassmorphism card, borderless, always-on-top, draggable.
  - **Double-click panel**: Seamlessly toggle between [3-Row Full Panel] and [1-Row Mini Capsule].
  - **Right-click menu**: Lock position, adjust polling frequency (250ms / 500ms / 1000ms), minimize to tray.
  - **Translucent Tooltip**: Hover over any row to view input/output tokens, reasoning tokens, cache reads, and invocation costs.
- **🔔 Windows System Tray Integration**:
  - Clicking [✕] in the top right automatically minimizes to the system notification tray with continuous background sampling.
  - **Left click / Double click tray icon**: Instantly toggle floating window visibility and bring it to the foreground.
  - **Hover tray icon**: Real-time balloon preview of the current foreground workspace and live Token/s speed.
- **⚡ Zero Intrusion & Minimal Overhead**:
  - Powered by SQLite WAL read-only non-blocking connection (`mode=ro`), zero modification to OpenCode source code or configuration files. Memory footprint ~20MB, CPU < 0.2%.

---

## 📝 Changelog

### 🚀 v1.1.0 (2026-10-26)

- **✨ New Features**:
  - **🎛️ Configurable Row Count (1–8 Rows)**: Break free from the fixed 3-row limit; freely configure list display rows (1 to 8 rows) in Settings, with adaptive elastic sizing for both full and mini capsule modes.
  - **📂 Dual Storage Modes (Portable / AppData)**: Added toggle for settings and log storage location, supporting out-of-the-box "Application Directory (Portable Mode)" and system standard "AppData Mode", with a one-click folder opening button.
  - **📍 Window Position Memory & Edge Snapping**: Automatically remembers screen position on close and restores on launch; auto-snaps within 15px of screen edges, with a one-click reset to top-right corner.
  - **🌓 Smooth Opacity Adjustment (30% – 100%)**: Added opacity slider in settings, supporting seamless adjustment from 30% translucent dark frosted glass to 100% opaque with live dynamic preview.
  - **🛑 Graceful Shutdown Script (`stop.bat`)**: Added a lightweight termination batch script to cleanly kill background `pythonw` monitor processes and prevent lingering tasks.
- **⚡ Optimizations**:
  - **🪟 Single-Instance Dialog Raising**: Repeatedly clicking "Settings" or "About" from tray or context menus will no longer open duplicate windows, but instead restores and raises the existing dialog.
  - **⚡ Instant Dropdown Opening**: Globally disabled Qt's slow sliding dropdown animation (`UI_AnimateCombo`), making polling interval and row count dropdowns open instantly with zero delay.
  - **🎨 Clean UI Layout & Polished Text**: Streamlined data path selection button to "Browse"; removed redundant path text box and dynamically display real active path directly beneath options for a compact layout.
  - **🚀 Zero-Overhead Native Topmost**: Eliminated redundant periodic Win32 topmost calls in refresh loops, relying purely on native OS window hierarchy for topmost priority with zero extra CPU and syscall overhead.
- **🐛 Bug Fixes**:
  - **🛡️ Fix Window Demoted Behind Other Apps**: Decoupled modal parent-child linkage between dialogs and main floating window, resolving Windows Win32 window ownership demotion issues.
  - **🔤 Fix Font Blurriness on High-DPI Displays**: Fixed stylesheet inheritance fallback to SimSun by globally standardizing on crisp `Microsoft YaHei UI` font while keeping native compact widget dimensions.
  - **⏱️ Fix TTFT Timing Baseline & Status Indicator**: Corrected streaming first-token baseline timing, clearly displaying animated `[⏳ Responding...]` breathing state prior to first token and eliminating misleading 0.0 tok/s.
  - **🐍 Fix Python 3.8 Compatibility Error**: Removed hard dependency on SQLite native `json_extract`, resolving JSON parse errors under stripped or minimal Python environments.

### 📦 v1.0.0 (2026-10-16)

- **✨ Initial Feature Release**:
  - **🖥️ Smart Multi-Window & Multi-Session Awareness**: 3-row session monitoring natively tracking active foreground OpenCode window/workspace and background active sessions.
  - **🛡️ Proprietary Anti-Burst True Rate Algorithm**: TTFT response breathing indicator, true steady streaming rate calculation, and burst-buffering anti-spoof protection.
  - **📌 Polished Capsule Widget Interaction**: Translucent dark card design, drag-and-drop, double-click toggle between 3-row full and 1-row mini capsule, right-click locking, and transparent tooltip telemetry.
  - **🔔 Windows System Tray Integration**: Minimize to tray with background sampling, balloon preview on hover, one-click wake/raise on left click, and context menu controls.
  - **⚡ Zero Intrusion & Minimal Overhead**: SQLite WAL read-only non-blocking parsing, zero code modification to OpenCode, CPU < 0.2%, memory ~20MB.

---

## 🛠️ Installation & Quick Start

### 1. Run from Source

#### Requirements
- Windows 10 / 11
- Python 3.8+

#### Install Dependencies
```bash
git clone https://github.com/your-username/opencode-token-monitor.git
cd opencode-token-monitor
pip install -r requirements.txt
```

#### Launch Desktop Floating Window (Default GUI Mode)
```bash
python main.py
```

#### Launch in 1-Row Mini Capsule Mode
```bash
python main.py --mini
```

#### Launch in CLI Terminal Monitor Mode
Run directly in the console without requiring any graphical display:
```bash
python main.py --cli
```

#### Custom Database Path or Refresh Interval
```bash
python main.py --db-path "C:/path/to/opencode.db" --interval 250
```

---

### 2. Standalone Portable Run (No Python Required)

For systems without a Python environment, use the pre-built standalone green release:
1. Open the [`dist/`](dist/) folder;
2. Double-click `OpenCodeTokenMonitor_v1.0.exe` to run immediately;
3. Or extract `OpenCodeTokenMonitor_v1.0_Portable.zip` to carry on a USB drive to any Windows PC.

---

## 📦 Build Executable

The project includes a one-click build script to package the app into a single standalone executable using PyInstaller:

```bash
python build.py
```

Upon completion, the standalone executable will be generated at `dist/OpenCodeTokenMonitor_v1.0.exe` with multi-resolution icons and tray support embedded.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
- Code style: Please follow PEP 8;
- Decoupled architecture: Keep core telemetry logic inside `core/` to ensure zero dependency on UI frameworks.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
