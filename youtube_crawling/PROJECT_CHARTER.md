# [개발 착수서] YouTube 일일 트렌드 분석 시스템

## 1. 프로젝트 개요
*   **프로젝트명**: YouTube Daily Trend Tracker
*   **목적**: 특정 키워드에 대해 전날(1일 전) 업로드된 영상의 메트릭(업로드 수, 조회수, 좋아요, 댓글)을 수집하여 시장의 화제성과 트렌드 변화를 수집/분석하는 자동화 시스템 구축.
*   **수행 기간**: 2026-01-14 ~ (진행 중)
*   **수행자**: Antigravity Agent & User

## 2. 프로젝트 목표 (Key Results)
1.  **안정적인 수집**: YouTube Data API v3를 활용하여 전날 업로드된 모든 영상을 누락 없이 검색.
2.  **데이터 정량화**: 단순 영상 수집을 넘어 조회수, 좋아요, 댓글 합계 및 평균 등 통계 데이터 산출.
3.  **영속성 확보**: 수집된 일일 집계 데이터를 데이터베이스(Supabase)에 실시간 적재하여 시계열 트렌드 관리.
4.  **분석 리포트**: 전일 대비 성장률(Growth Rate)과 반응도를 한눈에 파악할 수 있는 가공 데이터 생성.

## 3. 상세 개발 범위 (Feature Scope)
### 3.1 수집 모듈 (`crawler.py`)
*   지정된 키워드로 YouTube API를 호출하여 `publishedAfter`, `publishedBefore`를 활용한 날짜별 검색.
*   검색된 영상 ID를 기반으로 상세 통계(`statistics`) 리소스 확보.
*   다량의 데이터 처리를 위한 Pagination(NextPageToken) 처리.

### 3.2 저장 및 파이프라인 (`database.py`)
*   Supabase(PostgreSQL) 연동 및 일일 트렌드 테이블(`daily_trends`) 설계.
*   데이터 중복 방지 및 Upsert 로직 구현.

### 3.3 분석 모듈 (`analyzer.py`)
*   Pandas를 활용한 일계 데이터 집계.
*   전일 대비 반응 점수(Engagement Rate) 산출 로직 구현.

## 4. 기술 스택 (Tech Stack)
| 구분 | 기술 | 비고 |
| :--- | :--- | :--- |
| **언어** | Python 3.12 | |
| **외부 API** | YouTube Data API v3 | Google Cloud Console 기반 |
| **데이터 처리** | Pandas | 메트릭 집계 및 가공 |
| **인프라/DB** | Supabase | PostgreSQL 기반 시계열 데이터 저장 |
| **환경 설정** | Python-dotenv | API 키 및 접속 정보 보호 |

## 5. 데이터 스키마 (Draft)
### `daily_trends` 테이블
*   `id`: Primary Key
*   `date`: 분석 기준일 (YYYY-MM-DD)
*   `keyword`: 분석 키워드
*   `video_count`: 전날 업로드된 영상 총합
*   `total_views`: 총 조회수 합계
*   `total_likes`: 총 좋아요 합계
*   `total_comments`: 총 댓글 합계
*   `created_at`: 기록 생성 시간

## 6. 리스크 관리 및 대응
*   **YouTube API Quota**: 검색 결과가 많을 경우 API 할당량이 급격히 소모될 수 있음. 필요한 필드만 요청(`part="id,statistics"`)하여 할당량 최적화.
*   **데이터 누락**: 특정 시간대에 검색 결과가 안 나올 경우를 대비해 재시도 로직 및 에러 핸들링 포함.

---
**작성일**: 2026-01-14
**작성자**: Antigravity Agent
