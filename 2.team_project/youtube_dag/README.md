# YouTube 트렌드 수집 에어플로우(Airflow) DAG

특정 키워드에 대해 과거부터 현재까지의 유튜브 데이터를 수집하고, 이를 정기적으로 업데이트하는 Airflow 자동화 파이프라인입니다.

## 📁 디렉토리 구조

- `src/`: 데이터베이스 관리 모듈
- `scripts/`: 크롤러 로직 및 Airflow DAG 파일
- `docs/`: 프로젝트 산출물 문서 (구축서, 가이드 등)
- `config/`: (필요 시 점진적 추가)

## 🚀 시작하기

1. Airflow 환경에서 `scripts/qoxjf135_youtube_crawling_dag.py` 등록
2. `QOXJF135_YOUTUBE_API_KEY` 환경 변수 설정
3. Supabase 연결 설정 (conn_id: `qoxjf135_supabase_conn`)

## 🛠️ 기술 스택
- Python, Apache Airflow
- YouTube Data API v3
- Supabase (PostgreSQL)
