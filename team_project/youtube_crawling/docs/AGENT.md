# 🚀 YouTube Daily Trend Tracker

## 1. 프로젝트 개요
*   **목적**: YouTube Data API v3를 활용하여 특정 키워드에 대해 전날(1일전) 업로드된 영상들의 통계 데이터(업로드 수, 조회수, 좋아요 수, 댓글 수)를 수집하고 트렌드를 분석합니다.
*   **핵심 가치**: 일별 데이터 변화를 추적하여 키워드의 화제성과 확산 속도를 정량적으로 파악.

## 2. 기술 스택 (Tech Stack)
*   **Language**: Python 3.12+
*   **API**: Google API Client Library for Python (YouTube Data API v3)
*   **Data Processing**: Pandas, NumPy
*   **Database**: Supabase (PostgreSQL)
*   **Analysis**: Trend Analysis (Moving Average, Growth Rate)
*   **Environment**: `.env` 기반 비밀키 관리

## 3. 주요 기능 (Features)
1.  **일일 영상 통계 수집**: 특정 날짜(전날)에 업로드된 모든 영상 리스트 확보.
2.  **메트릭 분석**: 수집된 영상들의 조회수(Views), 좋아요(Likes), 댓글(Comments) 합계 및 평균 산출.
3.  **데이터 적재**: 날짜별 집계 데이터를 Supabase에 저장하여 시계열 데이터 구축.
4.  **트렌드 리포트**: 전일 대비 업로드 수 및 반응도 변화율 분석.

## 4. 단계별 이행 계획 (Roadmap)

### Step 1: 환경 설정 및 라이브러리 설치
- [ ] YouTube Data API v3 키 설정
- [ ] `google-api-python-client`, `python-dotenv`, `pandas` 설치
- [ ] `.env` 파일 설정

### Step 2: 트렌드 데이터 수집기 개발 (`crawler.py`)
- [ ] `publishedAfter` & `publishedBefore`를 활용한 날짜 지정 검색 로직
- [ ] `videos().list(part="statistics")`를 통한 상세 메트릭 수집
- [ ] 키워드별 일일 집계 데이터(전날 기준) 생성 기능

### Step 3: 데이터 파이프라인 구축 (`database.py`)
- [ ] Supabase 테이블 스키마 설계 (`daily_trends`)
- [ ] 일별 집계 데이터 적재 로직 구현

### Step 4: 분석 및 시각화 (`analyzer.py`)
- [ ] 전일 대비 성장률 분석 엔진 구현
- [ ] 트렌드 대시보드 시각화용 데이터 가공

---
*Updated by Antigravity Agent - 2026-01-14*