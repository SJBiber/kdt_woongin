# YouTube 인기 및 기록 데이터 분석 시스템

유튜브의 실시간 인기 급상승 영상과 과거 상위 영상들의 메트릭을 분석하고 키워드를 추출하여 저장하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 데이터 수집(Collector), 처리(Processor), DB(Database) 모듈
- `scripts/`: 메인 실행 스크립트 (main.py)
- `config/`: 설정 파일 (settings.py, .env, schema.sql)
- `docs/`: 프로젝트 문서 (AGENT.md)

## 🚀 시작하기

1. `config/.env`에 유튜브 API 키 및 Supabase 정보 설정
2. `scripts/main.py` 실행

## 🛠️ 기술 스택
- Python 3.12+
- YouTube Data API v3
- Supabase (PostgreSQL)
- Google API Client
