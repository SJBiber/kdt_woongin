# 🤖 Project: YouTube Trend AI Analyzer (YTAA) - v2.0
## AI 기반 카테고리 집계 및 통계 자동 분석 시스템

본 프로젝트는 `youtube` 분석기에서 수집된 데이터를 바탕으로, AI(Gemini)가 각 영상을 지능적으로 카테고리화하고, 해당 분야의 **점유율(영상 수)**과 **파급력(조회수 합계)**을 통계적으로 산출하는 고도화 시스템입니다.

---

## 1. 프로젝트 목표 (v2.0)
*   **Intelligent Categorization**: 단순 키워드 나열을 넘어, AI가 제목과 키워드 맥락을 분석해 최적의 대표 카테고리를 자동 할당.
*   **Quantitative Aggregation**: 카테고리별로 영상 개수와 총 조회수를 합산하여 실제 트렌드의 규모를 수치화.
*   **Structured JSON Pipeline**: AI 분석 결과를 즉시 DB에 적재할 수 있는 정형 데이터(JSON) 형태로 출력 및 자동화.

## 2. 주요 기능 및 프로세스

### A. DB 데이터 통합 로드
- `youtube_top_10` 테이블로부터 `TRENDING`(실시간) 및 `HISTORICAL`(주간 베스트) 각 20개 영상을 분석 대상(총 40개)으로 로드.

### B. AI 지능형 집계 엔진 (`src/ai_engine.py`)
- **사용 모델**: Google Gemini 2.0 Flash (Latest SDK)
- **작동 방식**:
    1. 각 영상의 제목, 조회수, 키워드를 AI에게 데이터셋으로 전달.
    2. AI가 각 영상을 '게임', '영화/드라마', '음악', '사회/뉴스' 등 상위 도메인으로 분류.
    3. 동일 카테고리 내의 **영상 수(video_count)**와 **조회수 합계(total_views)**를 자동 집계.
    4. 분석된 결과를 JSON 구조로 생성하여 파이프라인 전달.

### C. 데이터 적재 및 저장 (`youtube_category_trends` Table)
- AI가 생성한 통계 데이터를 새로운 전용 테이블에 저장하여 분석 히스토리 관리.
- **필드**: `category_name`, `video_count`, `total_views`, `representative_keywords`, `analysis_type`.

---

## 3. 개발 성과 및 현황 (Development Wins)

### ✅ [NEW] AI 카테고리 자동 분류 시스템
- 개별 키워드 리스트를 분석하여 "게임(+1)", "음악(+1)"과 같이 카테고리별 카운팅 및 조회수 합계 로직 구현 완료.
- 수집된 40개 영상을 대상으로 유의미한 도메인별 통계 데이터 생성 성공.

### ✅ [NEW] 最新 구글 GenAI SDK 전환
- 기존 `google-generativeai`를 최신 `google-genai` 라이브러리로 교체하여 성능 및 안정성 확보.

---

## 4. 필요 기술 스택 (Python Libraries)
1.  **`google-genai`**: 최신 Gemini 모델 연동 및 데이터 생성
2.  **`supabase`**: DB 연동(수집 데이터 로드 및 집계 데이터 저장)
3.  **`pandas`**: 대규모 데이터 전처리 및 결과 확인
4.  **`python-dotenv`**: 환경 변수 관리

---

## 5. 실행 결과 샘플
실행 시 다음과 같은 인사이트가 DB에 자동 적재됩니다.
- **[영화/드라마]**: 영상 6개, 총 조회수 1,853,864회
- **[사회/뉴스]**: 영상 4개, 총 조회수 8,407,842회
- **[게임]**: 영상 7개, 총 조회수 1,450,446회

---

**작성자**: Antigravity AI
**날짜**: 2026-01-08 (v2.0 Aggregation Edition 반영)
