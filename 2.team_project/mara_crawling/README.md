# 마라샹궈 네이버 블로그 검색 데이터 수집 시스템

'마라샹궈' 키워드에 대한 네이버 블로그 게시글 수를 정기적으로 수집하여 트렌드를 분석하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 재사용 가능한 모듈 (DB 관리 등)
- `scripts/`: 실행 및 테스트 스크립트
- `config/`: 설정 파일 (schema.sql, requirements.txt)
- `docs/`: 프로젝트 문서

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `scripts/crawler.py` 실행 (데이터 수집 및 CSV 저장)
3. `scripts/upload_to_db.py` 실행 (CSV 데이터를 DB로 업로드)

## 🛠️ 기술 스택
- Python 3.12+
- Supabase (PostgreSQL)
- Requests, Pandas
