# OpenCode Token Monitor (リアルタイム Token 速度・使用量監視ツール)

[English](README.md) | [简体中文](README_zh.md) | **日本語** | [한국어](README_ko.md)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Overhead](https://img.shields.io/badge/Overhead-CPU%20%3C%200.2%25-brightgreen.svg)]()

**OpenCode** 専用に設計された、軽量・ゼロ侵入・マルチウィンドウ認識対応のデスクトップフローティングモニター。フォアグラウンドプロジェクトおよびバックグラウンドセッションの Token/s スループット、初字レイテンシ（TTFT）、思考・推論トークン消費量、詳細メトリクスをリアルタイムで追跡・可視化します。

---

## 🌟 主な機能

- **🖥️ マルチウィンドウ＆マルチセッション自動認識（デフォルト 3 行表示）**：
  - **第 1 行【フォアグラウンド現在ウィンドウ】**：Windows ネイティブ API を利用し、現在アクティブ・フォーカスされている OpenCode ウィンドウおよびワークスペースを自動追跡。他のアプリケーションに切り替えた際は自動的に `[前台·挂起（フォアグラウンド保留）]` とマークし、メインタスクの処理速度を継続監視します。
  - **第 2・3 行【直近のアクティブウィンドウ】**：直近でアクティブなバックグラウンドセッションやサブタスク（Subagent）をリアルタイム表示。
- **🛡️ 独自開発の科学的レート計測・バースト誤認防止アルゴリズム (Anti-Burst Detection)**：
  - **TTFT 応答待機フェーズ**：プロンプト送信後、最初のトークンが返ってくるまでの待機時間中（キューイング、ゲートウェイ接続、Prefill 段階）は、誤解を招く `0.0 tok/s` ではなくアニメーションによる待機表示 `⏳ 响应中...（応答中...）` を表示。
  - **安定ストリーミング生成フェーズ（Decoding）**：最初のトークン受信後に TTFT を差し引き、モデル本来の正確なトークン出力速度（`⚡ 194.9 tok/s`）を算出。
  - **バーストバッファリング誤認防止ヒューズ**：リバースプロキシやゲートウェイの中継キャッシュにより、トークンが一括でまとめて送信された場合を自動検知。端点間の体感スループット（`📦 50.0 tok/s [整包]`）へと自動補正し、数千 tok/s のような虚偽の急上昇数値を排除します。
- **📌 洗練されたカプセル型 UI インターフェース**：
  - 半透明ダークグラスモーフィズムデザイン、枠なし、最前面固定表示、ドラッグによる自由な位置移動に対応。
  - **パネルのダブルクリック**：【3 行フル表示】と【1 行ミニカプセル表示】をワンタッチでシームレス切り替え。
  - **右クリックメニュー**：位置ロック（誤操作防止）、更新頻度調整（250ms / 500ms / 1000ms）、タスクトレイへの最小化。
  - **半透明ツールチップ**：任意の行にマウスホバーすると、入力/出力トークン数、推論トークン、キャッシュ読み取り量、API 利用コストを表示。
- **🔔 Windows システムトレイ（通知領域）完全対応**：
  - 右上の【✕】ボタンをクリックするとシステムトレイへ自動最小化し、バックグラウンドでの監視を継続。
  - **トレイアイコンの左クリック/ダブルクリック**：フローティングウィンドウの表示/非表示を瞬時に切り替え、最前面に復帰。
  - **トレイアイコンのマウスホバー**：現在のアクティブワークスペースとリアルタイムの Token/s 速度をツールチップでプレビュー。
- **⚡ 完全非侵入・極低リソース消費**：
  - SQLite WAL 読み取り専用ロックフリー接続（`mode=ro`）を採用。OpenCode のソースコードや設定ファイルを一切変更しません。メモリ使用量はわずか約 20MB、CPU 使用率は 0.2% 未満です。

---

## 🛠️ インストールと使い方

### 1. ソースコードから実行

#### 動作環境
- Windows 10 / 11
- Python 3.8+

#### 依存パッケージのインストール
```bash
git clone https://github.com/your-username/opencode-token-monitor.git
cd opencode-token-monitor
pip install -r requirements.txt
```

#### デスクトップフローティングウィンドウの起動 (デフォルト GUI モード)
```bash
python main.py
```

#### 1 行ミニカプセルモードで起動
```bash
python main.py --mini
```

#### CLI ターミナル監視モードで起動
GUI を使用せず、コマンドプロンプトや PowerShell の画面上で直接監視：
```bash
python main.py --cli
```

#### データベースパスや更新間隔のカスタマイズ
```bash
python main.py --db-path "C:/path/to/opencode.db" --interval 250
```

---

### 2. スタンドアロンポータブル版で実行 (Python 環境不要)

Python 環境がインストールされていない PC でも、ビルド済みのポータブル版ですぐに使用できます：
1. [`dist/`](dist/) ディレクトリを開きます。
2. `OpenCodeTokenMonitor_v1.0.exe` をダブルクリックするだけで即座に起動します。
3. または `OpenCodeTokenMonitor_v1.0_Portable.zip` を展開し、USB メモリ等で任意の Windows PC に持ち運んで利用可能です。

---

## 📦 実行ファイルのビルド (Build Executable)

本プロジェクトにはワンクリックで PyInstaller を実行できるビルドスクリプトが付属しています：

```bash
python build.py
```

ビルドが完了すると、`dist/OpenCodeTokenMonitor_v1.0.exe` に高解像度アイコンとシステムトレイ機能を内蔵した単一の実行可能ファイルが生成されます。

---

## 🤝 コントリビューション

Issue の報告や Pull Request を歓迎します！
- コード規約：PEP 8 に準拠してください。
- アーキテクチャの分離：UI フレームワークへの依存をなくすため、データ取得ロジックは必ず `core/` 配下に実装してください。

---

## 📄 ライセンス

本プロジェクトは [MIT License](LICENSE) のもとで公開されています。
