# 네이버 뉴스 댓글 수집 시스템 - 빠른 시작 가이드

## 📋 사전 준비

### 1. Supabase 설정

1. [Supabase](https://supabase.com)에 로그인
2. 새 프로젝트 생성
3. SQL Editor에서 `database/schema.sql` 파일의 내용을 실행하여 테이블 생성
4. Settings → API에서 다음 정보 확인:
   - `Project URL` (SUPABASE_URL)
   - `anon public` 키 (SUPABASE_KEY)

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp config/.env.example config/.env

# .env 파일 편집
nano config/.env
```

`.env` 파일 내용:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# 선택사항: 네이버 검색 API
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=

# 크롤링 설정
MAX_NEWS_COUNT=10
MAX_COMMENTS_PER_NEWS=100
```

### 3. ChromeDriver 설치

```bash
# Mac (Homebrew)
brew install chromedriver

# 설치 확인
chromedriver --version
```

## 🚀 실행 방법

### 기본 실행

```bash
python scripts/collect_comments.py
```

실행 후 키워드 입력:
```
검색 키워드를 입력하세요: AI
```

### 프로그래밍 방식

```python
import sys
from pathlib import Path

# 프로젝트 루트 추가
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.collect_comments import collect_and_save_comments

# 댓글 수집
collect_and_save_comments(
    keyword="인공지능",
    max_news=5,
    max_comments=50
)
```

## 📊 수집 프로세스

1. **뉴스 검색**: 키워드로 네이버 뉴스 검색
2. **URL 수집**: 네이버 뉴스 URL 목록 확보
3. **댓글 크롤링**: 각 뉴스의 댓글 수집
4. **중복 체크**: 이미 DB에 있는 댓글 필터링
5. **DB 저장**: 새로운 댓글만 Supabase에 저장

## 🔍 수집 결과 확인

Supabase Dashboard에서 확인:
1. Table Editor → `naver_news_comments` 선택
2. 수집된 댓글 데이터 확인

SQL 쿼리 예시:
```sql
-- 최근 수집된 댓글 10개
SELECT * FROM naver_news_comments 
ORDER BY created_at DESC 
LIMIT 10;

-- 특정 뉴스의 댓글
SELECT * FROM naver_news_comments 
WHERE news_id = 'your_news_id';

-- 공감 수가 많은 댓글
SELECT * FROM naver_news_comments 
ORDER BY likes DESC 
LIMIT 20;
```

## ⚠️ 문제 해결

### ChromeDriver 오류
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**해결**: ChromeDriver 설치 및 PATH 설정
```bash
brew install chromedriver
# 또는
brew upgrade chromedriver
```

### Supabase 연결 오류
```
ValueError: Supabase 설정이 필요합니다.
```

**해결**: `config/.env` 파일에 올바른 Supabase 정보 입력

### 댓글을 찾을 수 없음
```
⚠️ 댓글 영역을 찾을 수 없음
```

**원인**: 
- 댓글이 비활성화된 뉴스
- 네이버 뉴스 구조 변경

**해결**: 다른 키워드로 시도하거나 최신 뉴스 선택

## 📈 다음 단계

크롤링이 완료되면 다음 기능을 개발할 수 있습니다:

1. **감성 분석**: BERT 모델로 댓글 감정 분류
2. **키워드 추출**: 핵심 키워드 자동 추출
3. **LLM 분석**: DeepSeek 등으로 정밀 분석
4. **대시보드**: Streamlit으로 시각화

## 💡 팁

- **첫 실행**: 소량(5개 뉴스)으로 테스트 후 확대
- **크롤링 속도**: 뉴스 간 3초 대기로 서버 부하 최소화
- **중복 방지**: 동일 키워드 재실행 시 자동으로 새 댓글만 수집
- **헤드리스 모드**: 기본적으로 브라우저 창이 보이지 않음 (디버깅 시 `headless=False` 설정)
