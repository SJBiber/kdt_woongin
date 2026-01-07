# 🗓️ KDT Woongjin 학습 및 프로젝트 기록
---

## 🚀 프로젝트 타임라인 (Timeline)

### 📂 [2026-01-06] YouTube 트렌드 분석 및 시각화 시스템
*   **프로젝트 위치**: `ai/api/`, `ai/view/`
*   **목적**: 특정 키워드에 대한 YouTube 영상 데이터를 수집하고, 일별 통계 분석 및 시각화 대시보드를 제공하여 트렌드를 파악합니다.
*   **동작 원리 및 순서**:
    1.  **데이터 수집 (`youtube_search.py`)**: YouTube Data API v3를 활용, 페이지네이션을 처리하며 최대 1,000건의 영상 정보(제목, 날짜, 채널명)를 가져옵니다.
    2.  **상세 정보 매핑**: 수집된 각 영상 ID를 기반으로 별도의 API 호출을 통해 조회수(View Count) 데이터를 확보합니다.
    3.  **데이터 가공**: Pandas를 사용하여 날짜별 업로드 수와 조회수 총합을 집계하고 CSV 형식(`utf-8-sig`)으로 저장합니다.
    4.  **시각화 (`dashboard.py`, `viewer.py`)**: Tkinter와 Matplotlib을 연동하여 수집된 CSV를 불러와 일별 트렌드 차트와 상세 목록 뷰어를 제공합니다.
*   **결과**: '주식', '흑백요리사' 등 다양한 키워드에 대해 수집된 실절적인 트렌드 리포트와 시각화 툴을 얻을 수 있습니다.

### 📂 [2026-01-07 AM] 서울 지하철 실시간 데이터 적재 연구
*   **프로젝트 위치**: `studying/seoul_subway_monitoring/`
*   **목적**: 서울시 공공데이터 API와 Supabase(PostgreSQL) 클라우드 DB 연동의 기초 기술을 실습하고 데이터 스키마를 설계합니다.
*   **동작 원리 및 순서**:
    1.  **API 연동 (`ingest_subway.py`)**: 서울 열린데이터 광장의 실시간 열차 위치 API를 호출하여 JSON 데이터를 수신합니다.
    2.  **스키마 정의 (`schema.sql`)**: 수집된 정보의 효율적인 저장을 위해 초기 테이블 구조를 설계하고 인덱스를 구성합니다.
    3.  **검증 (`analysis_notebook.ipynb`)**: Jupyter Notebook을 통해 적재된 초기 데이터의 정합성을 확인합니다.
*   **결과**: 외부 API 데이터를 클린한 데이터베이스 형태로 구조화하여 적재하는 파이프라인 기초를 확보했습니다.

### 📂 [2026-01-07 PM] 서울 지하철 실시간 모니터링 & 분석 시스템 (고도화)
*   **프로젝트 위치**: `subway/seoul-subway-monitor/`
*   **목적**: 1~9호선 실시간 열차 위치 데이터를 전수 수집하여 배차 간격, 지연 구간, 회차 효율성 등 운영 지표를 도출하는 전문 모니터링 시스템입니다.
*   **동작 원리 및 순서**:
    1.  **배치 스케줄링 (`src/main.py`)**: `schedule` 라이브러리를 활용하여 1분 주기로 자동화된 수집 엔진을 상시 가동합니다.
    2.  **모듈형 API 클라이언트 (`src/api_client.py`)**: OOP 기반 설계로 서울시 API 호출 및 예외 처리를 담당하며, 대량의 데이터를 안정적으로 수집합니다.
    3.  **DB 최적화 (`src/db_client.py`)**: 수집된 데이터를 직관적인 영문 컬럼명으로 변환하고 Supabase에 실시간 Upsert 처리합니다.
    4.  **핵심 지표 분석 (`src/analysis/`)**:
        *   `dwell_time.py`: 역별 실제 정차 시간을 측정하여 지연 핫스팟 탐지.
        *   `interval_analysis.py`: 열차 간 간격을 분석하여 배차 정기성 확인.
        *   `turnaround_efficiency.py`: 종착역 회차 소요 시간을 분석하여 병목 지점 도출.
*   **결과**: 정적인 데이터를 넘어 '운영 효율성'을 실시간으로 추적할 수 있는 엔지니어링 기반의 지하철 대시보드 인프라를 구축했습니다.

---

## 🛠️ 기술 스택 (Tech Stack)
*   **Language**: Python 3.12+
*   **Database**: Supabase (PostgreSQL)
*   **Libraries**: Pandas, Requests, Supabase-py, Matplotlib, Tkinter, Schedule, Dotenv
