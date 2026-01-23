# YouTube 트렌드 추적 시스템

YouTube 영상들의 일별 통계 변화를 추적하여 관심도 추이를 분석하는 시스템입니다.

## 🚀 빠른 시작

```bash
# 1. 패키지 설치
pip install -r config/requirements.txt

# 2. config/.env 파일 설정
# (YouTube API 키, Supabase 정보)

# 3. 데이터베이스 스키마 실행
# Supabase SQL Editor에서 config/schema.sql 실행

# 4. 데이터 수집
cd scripts
python3 collect.py
```

## 📁 구조

- `src/` - 소스 코드
- `scripts/` - 실행 스크립트
- `config/` - 설정 파일
- `docs/` - 문서

## 📖 자세한 문서

전체 문서는 [`docs/README.md`](docs/README.md)를 참고하세요.

## 📊 현재 상태

- **수집 기간**: 2025-09-01 ~ 2026-01-22 (73일치)
- **총 영상 수**: 1,595개
- **총 조회수**: 3억 7,242만 회
