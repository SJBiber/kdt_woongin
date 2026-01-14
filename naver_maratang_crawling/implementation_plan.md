# 구현 계획안: 마라탕 네이버 크롤링

## 1. 개요
본 프로젝트는 '마라탕' 키워드의 과거 트렌드를 분석하기 위해 2018년부터 2023년까지 5년치 일별 블로그 포스팅 수를 네이버 Open API를 통해 수집합니다.

## 2. 기술 스택
- **Language**: Python 3.x
- **API**: Naver Search API (Blog)
- **Database**: Supabase
- **Environment Management**: `.env` (dotenv)

## 3. 주요 컴포넌트 구현 계획

### 3.1. Directory Structure
```
naver_maratang_crawling/
├── src/
│   ├── main.py          # 실행 메인 스크립트 (기간 및 키워드 제어, CSV 저장)
│   ├── scraper.py       # 네이버 AJAX 호출 및 데이터 가공 로직
│   └── requirements.txt  # 의존성 정의
├── maratang_blog_counts.csv # 최종 결과 파일
├── .env                 # API 키 (현재 방식에선 불필요하나 유지 가능)
├── task.md              # 할 일 목록
└── implementation_plan.md # 본 문서
```

### 3.2. 핵심 로직: 날짜별 데이터 수집
- 네이버 블로그 섹션의 AJAX 엔드포인트를 사용하여 기간별 `totalCount`를 직접 추출합니다.
- `startDate`와 `endDate`를 동일한 날짜로 설정하여 루프를 돌며 일별 데이터를 확보합니다.

### 3.3. 상세 설정
- **시작일**: 2018-08-01
- **종료일**: 2023-08-01
- **딜레이**: 실시간 차단 방지를 위해 각 요청 사이에 `time.sleep(0.5)` 지연 시간을 둡니다.

## 4. 데이터 저장
- 수집된 데이터는 `maratang_blog_counts.csv` 파일에 한 줄씩 추가(append)됩니다.
- 이는 수집 도중 오류가 발생하거나 중단되어도 이미 수집된 데이터를 보존하기 위함입니다.

## 5. 실행 방법
1. 관련 의존성 설치: `pip install -r src/requirements.txt`
2. 스크립트 실행: `python src/main.py`
