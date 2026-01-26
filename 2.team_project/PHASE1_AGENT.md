# Phase 1: 데이터 수집 및 크롤링 파이프라인 구축 계발 착수서

## 1. 프로젝트 개요
- **프로젝트명**: 서울시 '두쫀쿠(두바이 쫀득 쿠키)' 열풍의 경제적 실효성 및 수익성 분석
- **목표**: 소셜 데이터(네이버 블로그, 인스타그램) 크롤링을 통한 소비자 반응 수집 및 원자자 대비 마진율 산출을 위한 기초 데이터 확보
- **Phase 1 중점 사항**: 데이터 수집 자동화 기술(API & Crawling) 환경 구축 및 소스 코드 구현

## 2. Phase 1 개발 범위 (Data Acquisition)

### 2.1 Naver Search API 연동 (블로그 데이터)
- **목적**: '두바이 쫀득 쿠키' 관련 여론 및 핵심 키워드 추출
- **수집 대상**: 
    - `서울시 두바이 쫀득 쿠키`, `두쫀쿠 맛집`, `두쫀쿠 매장` 등
- **수집 항목**: 포스팅 제목, 본문 요약, 게시 날짜, 링크
- **기술 스택**: Python `requests`, Naver Open API

### 2.2 인스타그램 크롤링 (Playwright)
- **목적**: 이미지 중심의 트렌드 분석 및 해시태그 기반 위치 정보 수집
- **수집 대상**: 인스타그램 해시태그 검색 결과 및 인기 게시물
- **수집 항목**: 좋아요 수, 댓글 내용, 게시 날짜, 위치 태그(서울 지역 필터링)
- **기술 스택**: Python, Playwright (Headless 모드)

## 3. 프로젝트 기술 스택 및 환경 설정

| 구분 | 기술 스택 | 비고 |
|---|---|---|
| **언어** | Python 3.10+ | |
| **API** | Naver Search API | 블로그/카페 데이터 수집 |
| **Crawling** | Playwright | 인스타그램 동적 페이지 수집 |
| **Storage** | Local JSON / CSV | Phase 1 단계 (이후 DB 전환) |
| **Library** | pandas, requests | 데이터 핸들링 및 HTTP 통신 |

## 4. 상세 구현 계획 (Implementation Plan)

### Step 1: 환경 구성 및 인증 설정
- Naver Cloud Platform API Key 발급 및 `.env` 관리
- Playwright 브라우저 바이너리 설치 (`playwright install`)

### Step 2: Naver Blog Scraper 구현
- 검색어 필터링 logic 구현 (서울시 한정)
- 최근성 및 관련도 순 데이터 병합 로직

### Step 3: Instagram Scraper 구현
- 무한 스크롤(Infinite Scroll) 대응 로직
- 게시물 상세 페이지 진입 및 메타 데이터 추출

### Step 4: 데이터 정제 및 저장
- 중복 데이터 제거 (URL/PostID 기준)
- `data/raw/` 디렉토리에 일자별 저장

## 5. 예상 결과물 (Deliverables)
- `src/scrapers/naver_scraper.py`: 네이버 블로그 검색 API 모듈
- `src/scrapers/insta_scraper.py`: 인스타그램 Playwright 크롤러 모듈
- `requirements.txt`: 프로젝트 의존성 관리 파일
- `config.py`: API 설정 및 환경 변수 로더

---

## 6. Phase 1 체크리스트
- [x] Naver API 호출 성공 및 데이터 반환 확인
- [ ] 인스타그램 로그인 및 동적 데이터 로딩 성공 여부
- [x] 수집된 데이터의 인코딩 문제 해결 (한글 깨짐 방지)
- [ ] 데이터 수집 주기 설정 (Daily Batch 준비)
