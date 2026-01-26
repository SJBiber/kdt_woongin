# 네이버 블로그 검색 수집 에어플로우(Airflow) DAG

특정 키워드에 대한 네이버 블로그 포스팅 수를 정기적으로 수집하고 업데이트하는 Airflow 자동화 파이프라인입니다.

## 📁 디렉토리 구조

- `src/`: 유틸리티 및 수집 로직 모듈
- `scripts/`: Airflow DAG 파일
- `config/`: (환경 설정 관련 파일 예정)
- `docs/`: (프로젝트 문서 예정)

## 🚀 시작하기

1. Airflow 환경에서 `scripts/` 내의 DAG 파일 등록
2. Supabase 연결 설정 (conn_id: `kate29397_supabase_conn` 등)

## 🛠️ 기술 스택
- Python, Apache Airflow
- Naver Search API
- Supabase (PostgreSQL)
