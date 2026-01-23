# 📺 Project: Youtube Top 20 Analyzer

## 1. 프로젝트 개요
YouTube의 현재 인기 급상승 영상 상위 20개를 선정하여, 각 영상의 성과 지표(조회수, 좋아요 등)와 핵심 키워드를 정밀하게 분석하는 경량 데이터 수집 프로그램입니다.

- **대상**: 한국(KR) 지역 인기 급상승 상위 20개 영상
- **수집 항목**: 제목, 채널명, 조회수, 좋아요 수, 주요 키워드(태그 및 제목 기반)
- **저장소**: Supabase (PostgreSQL) 실시간 적재 및 히스토리 관리

### C. Historical High-View Analysis (New)
- 업로드 된 지 **최소 7일 이내** 영상 중 조회수가 가장 높은 상위 20개 추출
- 수집 항목: 조회수, 좋아요, **댓글 수**, 주요 키워드

## 3. 주요 기능 및 프로세스

### A. 인기 동영상 Top 20 추출
- YouTube Data API v3 (`Videos.list`)를 사용하여 `chart="mostPopular"` 기준으로 상위 20개 영상을 실시간으로 수집합니다.

### B. 장기 흥행 영상(Historical Top 20) 분석
- `search().list`와 `publishedAfter` 파라미터를 사용하여 최근 일주일 이내 업로드된 영상을 필터링합니다.
- `order="viewCount"` 옵션으로 누적 조회수가 가장 높은 영상을 선별합니다.

### B. 상세 메타데이터 수집
- **성과 지표**: `viewCount`, `likeCount` 데이터를 수집합니다.
- **알림 (싫어요 개수 관련)**: YouTube 공식 API 정책 및 2021년 업데이트로 인해 "싫어요(Dislike)" 개수는 일반 API 환경에서 더 이상 공개되지 않습니다. (필요 시 외부 라이브러리인 'Return YouTube Dislike' API 연동 검토 가능하나, 본 설계에서는 제외 또는 0으로 처리 안내)

### C. 주요 키워드 추출 (NLP/Tokenizing)
- 영상의 **제목(Title)**과 **태그(Tags)**를 분석합니다.
- 불용어를 제거하고 가장 빈번하게 등장하거나 핵심적인 키워드를 영상당 5개 내외로 선별합니다.

## 3. Tech Stack
- **Language**: Python 3.12
- **APIs**: YouTube Data API v3
- **Libraries**:
  - `google-api-python-client`: YouTube API 통신
  - `pandas`: 데이터 가공 및 CSV 저장
  - `python-dotenv`: API Key 관리
  - `re` (정규표현식): 키워드 정제

## 4. 데이터 구조 (Output Sample)
수집된 데이터는 `data/top10_analysis_YYYYMMDD.csv` 형태로 저장됩니다.

| 순위 | 제목 | 채널명 | 조회수 | 좋아요 | 주요 키워드 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [제목] | [채널] | 1,200,000 | 50,000 | 키워드1, 키워드2, ... |

## 5. 단계별 실행 계획
1. **환경 설정**: `configs/settings.py` 및 `.env` 파일 구성 (API Key 등록)
2. **수집기 구현**: `src/collector.py` 상위 10개 영상 및 상세 통계 수집 로직 구현
3. **키워드 분석기 구현**: `src/processor.py` 제목/태그 기반 키워드 추출 로직 구현
4. **메인 루틴 작성**: `main.py` 수집-분석-저장 프로세스 연결

---
**작성자**: Antigravity AI
**날짜**: 2026-01-08
