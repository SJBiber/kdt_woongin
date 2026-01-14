# 🚀 YouTube Deep Crawler & Sentiment Analyzer

## 1. 프로젝트 개요
*   **목적**: YouTube API의 할당량(Quota) 제한을 우회하여 특정 키워드나 채널의 대량 데이터를 수집하고, 특히 '댓글' 및 '반응' 데이터에 대한 심층 분석을 수행합니다.
*   **핵심 가치**: API로는 수집하기 까다로운 수천 개의 댓글 데이터 확보 및 감성 분석을 통한 여론 파악.

## 2. 기술 스택 (Tech Stack)
*   **Language**: Python 3.12+
*   **Scraping**: Playwright (Async 지원, 브라우저 자동화)
*   **Data Processing**: Pandas, NumPy
*   **Database**: Supabase (PostgreSQL)
*   **Analysis**: NLP (Sentiment Analysis), Word Cloud
*   **Environment**: `.env` 기반 비밀키 관리

## 3. 주요 기능 (Features)
1.  **키워드 기반 검색 결과 크롤링**: 광고를 제외한 연관 영상 리스트 자동 수집.
2.  **무한 스크롤 댓글 수집**: Playwright를 활용하여 특정 영상의 수천 개 댓글을 전수 수집.
3.  **데이터 정제 및 적재**: 중복 제거 및 이모지 처리 후 Supabase에 저장.
4.  **감성 분석 리포트**: 긍정/부정 비율 분석 및 핵심 키워드 시각화.

## 4. 단계별 이행 계획 (Roadmap)

### Step 1: 환경 설정 및 라이브러리 설치
- [ ] Playwright 및 브라우저 드라이버 설치
- [ ] `.env` 파일 설정 (Supabase 연동 정보)

### Step 2: 크롤러 엔진 개발 (`crawler.py`)
- [ ] 브라우저 Context 자동화 및 검색 기능 구현
- [ ] 영상 상세 정보 및 댓글 무한 스크롤 수집 로직 구현

### Step 3: 데이터 파이프라인 구축 (`database.py`)
- [ ] Supabase 테이블 스키마 설계 (`youtube_comments`, `video_meta`)
- [ ] 데이터 대량 업로드(Upsert) 기능 구현

### Step 4: 분석 및 시각화 (`analyzer.py`)
- [ ] 댓글 감성 분석 엔진 구현
- [ ] 대시보드용 데이터 가공

---
*Created by Antigravity Agent - 2026-01-13*