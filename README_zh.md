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

## 📝 更新日志 (Changelog)

### 🚀 v1.1.0 (2026-10-26)

- **✨ 新增功能 (New Features)**：
  - **🎛️ 会话行数自由配置 (1~8 行)**：打破原先固定 3 行限制，可在设置中自由调节列表展示行数（1~8 行可选），主面板与迷你胶囊模式尺寸自适应弹性伸缩。
  - **📂 存储路径双模式选择 (便携 / AppData)**：新增配置与日志存储位置切换，支持解压即用的“当前程序目录（便携模式）”与系统的“AppData 标准模式”，并支持一键打开存储文件夹。
  - **📍 窗口坐标记忆与屏幕边缘吸附**：自动记录关闭时的物理坐标位置，启动时无缝恢复；拖拽至屏幕边缘 15px 内自动贴边对齐，并提供一键复位至右上角。
  - **🌓 不透明度平滑调节 (30% ~ 100%)**：设置面板新增透明度滑块，支持 30% 半透磨砂到 100% 不透明的平滑拖动与实时动态预览。
  - **🛑 配套优雅退出脚本 (`stop.bat`)**：新增轻量退出批处理脚本，一键彻底退出后台 `pythonw` 监控进程，杜绝后台进程残留。
- **⚡ 优化改进 (Optimizations)**：
  - **🪟 设置与关于窗口单例唤醒**：重复点击托盘或右键菜单中的“设置/关于”不再重复弹出新窗口，而是自动恢复并置顶激活已有窗口。
  - **⚡ 下拉选项瞬时秒开响应**：全局禁用 Qt 底层下拉滑动动画（`UI_AnimateCombo`），点击“采样频率”与“显示行数”下拉选项实现 0 延迟即点即显。
  - **🎨 界面排版与文案细节打磨**：数据源配置按钮精简为“浏览”；移除底部冗余大框，直接在选项下方展示动态真实路径，布局更加紧凑整洁。
  - **🚀 零开销原生常驻置顶**：移除数据轮询刷新中多余的系统级置顶调用，纯依靠操作系统底层机制维持顶层常驻，零额外 CPU 与系统调用负担。
- **🐛 缺陷修复 (Bug Fixes)**：
  - **🛡️ 修复浮窗被其他软件遮挡置底问题**：排查并解除设置与关于弹窗与主浮窗的底层父子绑定，彻底根治 Windows 窗口所有权冲突导致的悬浮窗降级问题。
  - **🔤 修复高分屏字体模糊发虚问题**：排查并消除样式继承缺失导致系统回退宋体的问题，全局统一应用现代高清 `Microsoft YaHei UI` 字体，且窗口尺寸保持精致不膨胀。
  - **⏱️ 修复首字延迟 (TTFT) 计算基准与状态显示**：修正流式首字耗时计算基准，首字到达前明确展示 `[⏳ 响应中...]` 呼吸态，杜绝误导性的 0.0 tok/s。
  - **🐍 修复 Python 3.8 兼容性报错**：移除对 SQLite 原生 `json_extract` 函数的硬依赖，彻底解决部分精简 Python 环境下的数据库解析报错。

### 📦 v1.0.0 (2026-10-16)

- **✨ 核心功能初始发布**：
  - **🖥️ 多窗口与多会话智能感知**：支持 3 行会话展示，原生追踪 Windows 前台当前聚焦的 OpenCode 工作区及后台活跃会话。
  - **🛡️ 独家防虚标科学速率算法 (Anti-Burst Detection)**：支持首字等待阶段呼吸指示、真实平稳流式速率计算与突发整包缓冲防伪熔断。
  - **📌 类似输入法胶囊的精致交互**：半透明毛玻璃暗黑卡片设计，支持拖拽、双击切换 3 行完整面板与单行迷你胶囊模式、右键锁定与全透明 Tooltip 明细。
  - **🔔 Windows 系统托盘深度整合**：支持最小化至通知区域后台采样、托盘悬浮气泡预览、左键一键唤醒置顶与右键快捷菜单。
  - **⚡ 零侵入极低开销**：基于 SQLite WAL 只读无锁连接解析，对 OpenCode 零修改零侵入，CPU < 0.2%，内存 ~20MB。

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
