# 서울 지하철 데이터 수집 및 분석 실습

서울시 공공데이터 API와 Supabase를 활용하여 지하철 위치 데이터를 수집하고 분석하는 기초적인 실습 프로젝트입니다.

## 📁 디렉토리 구조

- `scripts/`: 데이터 수집 스크립트 (.py) 및 분석 노트북 (.ipynb)
- `config/`: 설정 파일 (.env, schema.sql, requirements.txt)
- `docs/`: 실습 관련 메모 및 문서

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env`에 서울시 데이터 API 키 및 Supabase 정보 설정
3. `python scripts/ingest_subway.py --line 2호선` 실행

## 🛠️ 기술 스택
- Python 3.12+
- Seoul Open Data API
- Supabase (PostgreSQL)
- Jupyter Notebook
