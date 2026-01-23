# YouTube 일일 트렌드 분석 시스템

특정 키워드에 대해 전날 업로드된 영상들의 메트릭을 수집하여 시장의 반응 속도와 트렌드 변화를 분석하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 재사용 가능한 모듈 (DB 관리 등)
- `scripts/`: 메인 실행 스크립트 (크롤러)
- `config/`: 설정 파일 (.env, schema.sql, requirements.txt)
- `docs/`: 프로젝트 문서 (개발 착수서 등)

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env` 파일에 API 키 설정
3. `scripts/crawler.py` 실행

## 🛠️ 기술 스택
- Python 3.12+
- Supabase (PostgreSQL)
- YouTube Data API v3
- Pandas, google-api-python-client
