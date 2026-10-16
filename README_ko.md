# OpenCode Token Monitor (실시간 Token 속도 및 사용량 플로팅 모니터)

[English](README.md) | [简体中文](README_zh.md) | [日本語](README_ja.md) | **한국어**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Overhead](https://img.shields.io/badge/Overhead-CPU%20%3C%200.2%25-brightgreen.svg)]()

**OpenCode** 전용으로 제작된 가볍고 시스템 부하가 거의 없는 다중 창 인식 데스크톱 플로팅 모니터입니다. 현재 포그라운드 작업 및 백그라운드 세션의 Token/s 처리 속도, 첫 토큰 응답 시간(TTFT), 추론 토큰 사용량 및 상세 호출 지표를 실시간으로 모니터링합니다.

---

## 🌟 주요 기능

- **🖥️ 다중 창 및 다중 세션 지능형 감지 (기본 3행 표시)**:
  - **1행【포그라운드 활성 창】**: Windows 기본 API를 활용하여 현재 활성화 및 포커스된 OpenCode 창과 작업 공간을 자동으로 추적합니다. 다른 응용 프로그램으로 전환할 경우 자동으로 `[前台·挂起 (포그라운드 일시 대기)]` 상태로 전환되며, 메인 작업의 처리량을 지속적으로 캡처합니다.
  - **2·3행【최근 활성 창】**: 포그라운드 세션 외에 가장 최근에 동작한 백그라운드 세션 또는 서브태스크(Subagent)를 실시간으로 표시합니다.
- **🛡️ 독자적인 허위 수치 방지 과학적 속도 측정 알고리즘 (Anti-Burst Detection)**:
  - **TTFT 응답 대기 단계**: 요청 전송 후 첫 번째 토큰이 반환될 때까지의 대기 시간(대기열, 게이트웨이 핸드셰이크, Prefill 단계) 동안 오해를 불러일으킬 수 있는 `0.0 tok/s` 대신 동적 애니메이션 표시인 `⏳ 响应中... (응답 중...)`을 제공합니다.
  - **안정적인 스트리밍 생성 단계 (Decoding)**: 첫 번째 토큰이 도착한 후 TTFT를 차감하여 모델 본연의 정확한 스트리밍 토큰 생성 속도(`⚡ 194.9 tok/s`)를 계산합니다.
  - **버스트 버퍼링 허위 수치 방지 퓨즈**: 프록시나 게이트웨이 중간 버퍼링으로 인해 토큰이 한꺼번에 쏟아져 들어올 때 비정상적인 버스트를 감지하고, 실제 체감 속도(`📦 50.0 tok/s [整包]`)로 자동 보정하여 수천 tok/s에 달하는 과장된 수치를 배제합니다.
- **📌 완성도 높은 캡슐형 플로팅 UI 및 인터랙션**:
  - 반투명 다크 글래스모피즘 카드 디자인, 프레임리스, 항상 위 고정, 마우스 자유 드래그 지원.
  - **패널 더블 클릭**: [3행 전체 패널]과 [1행 미니 캡슐] 모드를 손쉽게 전환.
  - **마우스 우클릭 메뉴**: 위치 고정(오작동 방지), 새로고침 주기 설정(250ms / 500ms / 1000ms), 시스템 트레이로 최소화.
  - **반투명 툴팁**: 각 행에 마우스를 올리면 입력/출력 토큰, 추론 토큰, 캐시 읽기 양 및 호출 비용을 즉시 확인.
- **🔔 Windows 시스템 트레이(알림 영역) 완벽 연동**:
  - 패널 우측 상단의 [✕] 버튼을 클릭하면 시스템 트레이로 최소화되며 백그라운드 샘플링이 계속 유지됩니다.
  - **트레이 아이콘 클릭/더블 클릭**: 플로팅 창 표시/숨김을 원클릭으로 전환하고 항상 최상단으로 호출.
  - **트레이 아이콘 마우스 호버**: 현재 활성 작업 공간과 실시간 Token/s 속도를 풍선 도움말(Tooltip)로 미리보기.
- **⚡ 비침투적 설계 및 극히 낮은 시스템 점유율**:
  - SQLite WAL 읽기 전용 락프리 연결(`mode=ro`)을 기반으로 하여 OpenCode 소스 코드나 설정 파일을 전혀 수정하지 않습니다. 메모리 점유율 약 20MB, CPU 점유율 0.2% 미만.

---

## 🛠️ 설치 및 빠른 시작

### 1. 소스 코드에서 실행

#### 요구 사항
- Windows 10 / 11
- Python 3.8+

#### 의존 패키지 설치
```bash
git clone https://github.com/your-username/opencode-token-monitor.git
cd opencode-token-monitor
pip install -r requirements.txt
```

#### 데스크톱 플로팅 모니터 실행 (기본 GUI 모드)
```bash
python main.py
```

#### 1행 미니 캡슐 모드로 실행
```bash
python main.py --mini
```

#### 순수 CLI 터미널 모니터링 모드로 실행
그래픽 화면 없이 명령 프롬프트나 터미널에서 직접 실행:
```bash
python main.py --cli
```

#### 데이터베이스 경로 또는 새로고침 주기 직접 지정
```bash
python main.py --db-path "C:/path/to/opencode.db" --interval 250
```

---

### 2. 무설치 포터블 버전으로 실행 (Python 설치 불필요)

Python 환경이 없는 PC에서는 미리 빌드된 독립 실행 파일을 바로 사용할 수 있습니다:
1. [`dist/`](dist/) 폴더로 이동합니다.
2. `OpenCodeTokenMonitor_v1.0.exe`를 더블 클릭하여 즉시 실행합니다.
3. 또는 `OpenCodeTokenMonitor_v1.0_Portable.zip` 파일의 압축을 풀어 USB 메모리에 담아 다른 Windows PC에서 즉시 사용할 수 있습니다.

---

## 📦 실행 파일 직접 빌드 (Build Executable)

본 프로젝트는 PyInstaller를 이용해 단일 실행 파일로 패키징할 수 있는 원클릭 빌드 스크립트를 제공합니다:

```bash
python build.py
```

빌드가 완료되면 고해상도 아이콘과 트레이 기능이 내장된 독립 실행 파일이 `dist/OpenCodeTokenMonitor_v1.0.exe`에 생성됩니다.

---

## 🤝 기여 안내

이슈 제보 및 풀 리퀘스트(Pull Request)를 언제나 환영합니다!
- 코드 스타일: PEP 8 표준을 준수해 주세요.
- 아키텍처 분리: UI 종속성을 배제하기 위해 핵심 텔레메트리 로직은 반드시 `core/` 내부에 구현해 주세요.

---

## 📄 라이선스

본 프로젝트는 [MIT License](LICENSE)에 따라 오픈소스로 제공됩니다.
