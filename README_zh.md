# OpenCode Token Monitor (实时速率与用量悬浮监控器)

[English](README.md) | **简体中文** | [日本語](README_ja.md) | [한국어](README_ko.md)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Overhead](https://img.shields.io/badge/Overhead-CPU%20%3C%200.2%25-brightgreen.svg)]()

专为 **OpenCode** 打造的轻量级、零侵入、多窗口感知桌面悬浮监控器。实时监控当前前台项目与后台会话的 Token/s 吞吐速率、首字延迟（TTFT）、思考推理用量与调用明细。

---

## 🌟 核心特性

- **🖥️ 多窗口与多会话智能感知（默认 3 行）**：
  - **第 1 行【前台当前窗口】**：自动调用 Windows 原生 API 追踪当前激活聚焦的 OpenCode 窗口及工作区。切换到外部其他软件时，自动标记为 `[前台·挂起]`，持续捕获主任务吞吐。
  - **第 2、3 行【最近活动窗口】**：实时呈现除前台外最近活跃的后台会话或子任务（Subagent）。
- **🛡️ 独家防虚标科学速率算法 (Anti-Burst Detection)**：
  - **等待响应阶段（TTFT）**：在发送请求到首个 Token 返回前（排队、网关握手、Prefill 阶段），显示动态呼吸态 `⏳ 响应中...`，拒绝显示误导性的 `0.0 tok/s`。
  - **平稳流式阶段（Decoding）**：首字到达后扣除 TTFT，精准呈现模型真实的流式吐字速率（`⚡ 194.9 tok/s`）。
  - **突发缓冲防伪熔断**：当遭遇服务端/网关反代中途缓冲、最后一口气整包推送时，自动识别突发异常并以端到端实际体感速率呈现（`📦 50.0 tok/s [整包]`），杜绝动辄上千 Token/s 的虚假数字。
- **📌 类似输入法胶囊的精致交互**：
  - 半透明毛玻璃暗黑卡片、无边框、置顶显示、鼠标自由拖拽。
  - **双击面板**：在【3 行完整面板】与【单行迷你胶囊】之间无缝切换。
  - **鼠标右键**：快速锁定位置（防误触）、调节刷新率（250ms/500ms/1000ms）、最小化到托盘。
  - **全透明 Tooltip**：鼠标悬停任一行，查看详细输入/输出 Token、推理 Token、缓存读取量及调用费用。
- **🔔 Windows 系统托盘（通知区域）深度整合**：
  - 点击面板右上角【✕】自动最小化到托盘，后台持续采样。
  - **左键单击/双击托盘小图标**：一键切换悬浮窗显示与隐藏，并自动带到最前端。
  - **悬浮托盘图标**：实时弹出 Tooltip 气泡预览当前前台工作区与实时 Token 吐字速率。
- **⚡ 零侵入极低开销**：
  - 基于 SQLite WAL 只读无锁连接（`mode=ro`），完全不修改 OpenCode 源码或配置文件，内存占用 ~20MB，CPU < 0.2%。

---

## 🛠️ 安装与快速上手

### 1. 从源码运行

#### 环境要求
- Windows 10 / 11
- Python 3.8+

#### 安装依赖
```bash
git clone https://github.com/your-username/opencode-token-monitor.git
cd opencode-token-monitor
pip install -r requirements.txt
```

#### 启动桌面悬浮窗 (默认 GUI 模式)
```bash
python main.py
```

#### 以单行迷你胶囊模式启动
```bash
python main.py --mini
```

#### 以纯命令行终端监控模式启动 (CLI Mode)
无需任何图形界面环境，直接在终端中实时监控输出：
```bash
python main.py --cli
```

#### 自定义数据库路径或刷新频率
```bash
python main.py --db-path "C:/path/to/opencode.db" --interval 250
```

---

### 2. 便携独立运行 (无需安装 Python)

若在没有 Python 环境的电脑上使用，直接使用已打包好的绿色免安装版：
1. 进入 [`dist/`](dist/) 目录；
2. 双击运行 `OpenCodeTokenMonitor_v1.0.exe` 即可直接使用；
3. 或解压 `OpenCodeTokenMonitor_v1.0_Portable.zip` 携带到任意 Windows 电脑运行。

---

## 📦 自行构建打包 (Build Executable)

项目自带一键打包脚本，执行以下命令即可自动使用 PyInstaller 生成单文件免安装 EXE：

```bash
python build.py
```

构建完成后，独立的 EXE 文件将自动生成于 `dist/OpenCodeTokenMonitor_v1.0.exe`，并内嵌专属的多分辨率图标与托盘组件。

---

## 🤝 贡献与交流

欢迎提交 Issue 或 Pull Request！
- 代码规范：建议遵循 PEP 8；
- 模块解耦：非界面逻辑请务必封装在 `core/` 下，确保核心遥测逻辑对 GUI 零依赖。

---

## 📄 开源许可证
 
本项目基于 [MIT License](LICENSE) 开源。
