# 지그재그(Zigzag) 상품 및 리뷰 데이터 수집 시스템

여성 패션 플랫폼 '지그재그'의 카테고리별 상품 정보와 실사용 리뷰 데이터를 자동으로 수집하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 핵심 수집 및 DB 연동 모듈 (Playwright 기반)
- `scripts/`: 메인 실행 스크립트 (main.py)
- `config/`: 설정 파일 (.env, setup_schema.sql, settings.py)
- `docs/`: 프로젝트 산출물 문서
- `config/data/`: (선택) 로컬 백업용 JSON 데이터

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `playwright install chromium` 실행 (브라우저 설치)
3. `config/.env`에 Supabase 정보 설정
4. `scripts/main.py` 실행

## 🛠️ 기술 스택
- Python 3.12+
- Playwright (Web Scraping)
- Supabase (PostgreSQL)
- Asyncio, Pandas
