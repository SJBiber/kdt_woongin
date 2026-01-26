# 네이버 뉴스 댓글 수집 시스템

네이버 뉴스 댓글을 키워드 기반으로 수집하고 Supabase에 저장하는 시스템입니다.

## 📋 주요 기능

- ✅ 키워드 기반 네이버 뉴스 검색
- ✅ 동적 크롤링을 통한 댓글 수집
- ✅ Supabase 데이터베이스 자동 저장
- ✅ 중복 댓글 자동 필터링
- ✅ 네이버 검색 API 지원 (선택사항)

## 🛠️ 기술 스택

- **Python 3.12**
- **Selenium** (동적 크롤링)
- **BeautifulSoup4** (HTML 파싱)
- **Supabase** (데이터베이스)

## 📦 설치 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. ChromeDriver 설치

Selenium 사용을 위해 ChromeDriver가 필요합니다:

```bash
# Homebrew 사용 (Mac)
brew install chromedriver

# 또는 수동 다운로드
# https://chromedriver.chromium.org/downloads
```

### 3. 환경 변수 설정

`config/.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
cp config/.env.example config/.env
```

`.env` 파일 내용 수정:

```env
# 필수: Supabase 설정
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# 선택: 네이버 검색 API (없으면 크롤링 방식 사용)
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

# 크롤링 설정
MAX_NEWS_COUNT=10
MAX_COMMENTS_PER_NEWS=100
```

### 4. Supabase 테이블 생성

`database/schema.sql` 파일의 SQL을 Supabase SQL Editor에서 실행하여 테이블을 생성합니다.

## 🚀 사용 방법

### 기본 사용

```bash
python scripts/collect_comments.py
```

실행 후 검색 키워드를 입력하면 자동으로 뉴스 검색 → 댓글 수집 → DB 저장이 진행됩니다.

### 프로그래밍 방식 사용

```python
from scripts.collect_comments import collect_and_save_comments

# 키워드로 댓글 수집
collect_and_save_comments(
    keyword="AI",
    max_news=5,
    max_comments=50
)
```

## 📁 프로젝트 구조

```
naver_news_comment_cr/
├── config/              # 환경 설정
│   ├── .env.example     # 환경 변수 템플릿
│   └── settings.py      # 설정 로드 모듈
├── database/            # 데이터베이스
│   ├── schema.sql       # 테이블 스키마
│   └── supabase_manager.py  # DB 관리 모듈
├── src/
│   ├── collector/       # 수집 모듈
│   │   ├── news_searcher.py     # 뉴스 검색
│   │   └── comment_crawler.py   # 댓글 크롤링
│   ├── analyzer/        # 분석 모듈 (추후 개발)
│   └── utils/           # 유틸리티
├── scripts/             # 실행 스크립트
│   └── collect_comments.py  # 메인 수집 스크립트
├── docs/                # 문서
├── requirements.txt     # 패키지 의존성
├── AGENT.md            # 프로젝트 가이드
└── 설계서.md            # 설계 문서
```

## 📊 데이터베이스 스키마

`naver_news_comments` 테이블:

| 필드 | 타입 | 설명 |
|------|------|------|
| comment_id | TEXT | 댓글 고유 ID (PK) |
| news_id | TEXT | 뉴스 기사 ID |
| author | TEXT | 작성자 |
| content | TEXT | 댓글 내용 |
| likes | INTEGER | 공감 수 |
| dislikes | INTEGER | 비공감 수 |
| published_at | TIMESTAMP | 작성 시간 |
| sentiment_label | INTEGER | BERT 분석 결과 (0:긍정, 1:부정, 2:중립) |
| sentiment_score | FLOAT | 분석 확신도 |
| llm_sentiment | INTEGER | LLM 분석 결과 |
| keywords | TEXT[] | 키워드 리스트 |
| created_at | TIMESTAMP | 데이터 생성 시간 |

## ⚠️ 주의사항

1. **크롤링 속도**: 네이버 서버 부하를 고려하여 뉴스 간 3초 간격을 두고 수집합니다.
2. **ChromeDriver**: Selenium 사용을 위해 Chrome 브라우저와 ChromeDriver가 필요합니다.
3. **댓글 제한**: 일부 뉴스는 댓글이 비활성화되어 있을 수 있습니다.
4. **중복 방지**: 동일한 댓글은 자동으로 필터링되어 저장되지 않습니다.

## 🔜 향후 개발 예정

- [ ] 감성 분석 (BERT + LLM)
- [ ] 키워드 추출
- [ ] 대시보드 시각화
- [ ] 스케줄링 자동화

## 📝 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.
