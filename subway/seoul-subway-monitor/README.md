# 서울 지하철 실시간 모니터링 시스템

서울시 열차 실시간 위치 API를 활용하여 각 호선별 열차 운행 현황을 수집하고 분석하는 시스템입니다.

## 📁 디렉토리 구조

- `src/`: API 연동 및 DB 클라이언트 모듈
- `scripts/`: 데이터 수집 메인 프로그램 및 분석 스크립트
- `config/`: 설정 파일 (.env, config.py, requirements.txt)
- `docs/`: 프로젝트 기술 문서 및 가이드

## 🚀 시작하기

1. `config/requirements.txt` 설치
2. `config/.env`에 서울시 Open API 키 및 Supabase 정보 설정
3. `python scripts/main.py` 실행 (1분마다 위치 수집)

## 🛠️ 기술 스택
- Python 3.12+
- Seoul Open API (Realtime Position)
- Supabase (PostgreSQL)
- Schedule, Requests
