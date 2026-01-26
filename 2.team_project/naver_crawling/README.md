# 네이버 블로그 검색 데이터 수집 시스템

네이버 Search API를 활용하여 특정 키워드에 대한 블로그 게시글 수의 변화를 추적하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 핵심 로직 (스크래퍼, DB 연동)
- `scripts/`: 실행 프로그램 (수집기, 서빙 앱)
- `config/`: 설정 파일 (SCHEMA.sql, requirements.txt, .env)
- `docs/`: 개발 문서

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env`에 네이버 API 키 및 Supabase 정보 설정
3. `scripts/main.py` 실행 (데이터 수집)
4. `streamlit run scripts/app.py` 실행 (대시보드 확인)

## 🛠️ 기술 스택
- Python 3.12+
- Naver Search API
- Supabase (PostgreSQL)
- Streamlit, Pandas
