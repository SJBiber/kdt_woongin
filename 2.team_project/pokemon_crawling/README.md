# 포켓몬 빵 관련 블로그 검색 데이터 수집 시스템

포켓몬스터 빵 관련 키워드에 대한 네이버 블로그 검색 결과 수 추이를 수집하여 트렌드 지표로 활용하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 재사용 가능한 모듈 (DB 관리 등)
- `scripts/`: 데이터 수집 및 업로드 스크립트
- `config/`: 설정 파일 (schema.sql, requirements.txt, .env)
- `docs/`: 프로젝트 문서

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env`에 Supabase 정보 설정
3. `scripts/crawler.py` 실행 (데이터 수집)
4. `scripts/upload_to_db.py` 실행 (데이터 업로드)

## 🛠️ 기술 스택
- Python 3.12+
- Supabase (PostgreSQL)
- Requests, Pandas
