# 네이버 키워드 기반 블로그 수집 시스템

특정 키워드(마라탕, 탕후루 등)에 대한 네이버 블로그 검색 결과 수를 대량으로 수집하고 분석하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: 핵심 수집 및 DB 연동 모듈
- `scripts/`: 실행 및 통계 스크립트
- `config/`: 설정 파일 (requirements.txt, .env)
- `docs/`: 프로젝트 산출물 문서
- `data/`: 수집된 CSV 데이터 파일

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env`에 Supabase 정보 설정
3. `scripts/main.py` 실행 (데이터 수집 및 CSV/DB 저장)
4. `streamlit run scripts/app.py` 실행 (대시보드 시각화)

## 🛠️ 기술 스택
- Python 3.12+
- Supabase (PostgreSQL)
- Naver Blog Search, Streamlit
