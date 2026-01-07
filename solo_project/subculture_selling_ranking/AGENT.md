# [Project Plan] 한국 서브컬쳐 게임 시장 현황 및 매출 분석 (KR Subculture Market Intelligence)

이 문서는 **한국 국내 시장**을 중심으로 서브컬쳐(모바일/가챠) 게임의 시장 현황과 매출 데이터를 추출, 저장, 분석하기 위한 데이터 엔지니어링 및 분석 설계서입니다.

---

## 1. 프로젝트 개요
- **목표**: 한국 내 주요 서브컬쳐 게임(블루 아카이브, 승리의 여신: 니케, 원신, 붕괴: 스타레일 등)의 매출 추이 및 유저 동향 분석
- **핵심 지표 (KPI)**: 국내 구글 플레이/앱스토어 매출 순위, 추정 매출량, 국내 커뮤니티(아카라이브, 루리웹 등) 반응도 및 업데이트 연계 효율

## 2. 기술 스택 (Tech Stack)

### **Core**
- **Language**: Python 3.x
- **Database**: Supabase (PostgreSQL)
- **Data Processing**: Pandas, NumPy

### **Data Extraction (한국 시장 특화 추출)**
- **Market Data**: 
  - **Mobile Index (모바일인덱스)**: 국내 앱 마켓 통합 매출 및 MAU 데이터 (Scraping/Crawling)
  - **Google Play / App Store (KR) Top Grossing**: 실시간 국내 매출 순위 데이터
- **Community & News**:
  - **Naver News API**: 게임 관련 국내 기사 및 보도자료 수집
  - **Community Scraping**: 아카라이브(채널별 인기글), 인벤 등 국내 서브컬쳐 커뮤니티 여론 수집
- **Automation**: GitHub Actions

### **Visualization (시각화)**
- **Streamlit**: 국내 시장 모니터링 대시보드
- **Plotly/Matplotlib**: 시각화 라이브러리

---

## 3. 데이터 추출 전략 (Data Ingestion)

한국 시장은 특정 플랫폼의 의존도가 높고 커뮤니티 여론이 매출에 즉각 반영되는 특징이 있습니다.

| 데이터 소스 | 추출 방법 | 주요 데이터 |
| :--- | :--- | :--- |
| **모바일인덱스 (KR)** | BeautifulSoup/Playwright | 국내 안드로이드+iOS 통합 매출 순위 및 추정 매출 |
| **Google Play (KR)** | Playwright 크롤링 | 한국 지역 실시간 매출 순위 및 사용자 리뷰 |
| **Naver Search Trend** | Naver DataLab API | 게임별 검색량 추이 (화제성 분석) |
| **국내 대형 커뮤니티** | Scrapy / BeautifulSoup | 픽업/이벤트 관련 유저 여론 (긍정/부정 감성 분석) |

---

## 4. 데이터베이스 설계 (Supabase Schema)

한국 시장 특화 정보를 포함하도록 설계합니다.

### **Table: `kr_games`**
- `id` (uuid, PK)
- `title` (text): 게임명
- `publisher_kr` (text): 국내 서비스사 (예: 넥슨, 카카오게임즈 등)
- `genre` (text): 세부 장르 (수집형 RPG, 액션 등)

### **Table: `kr_market_stats`**
- `id` (bigint, PK)
- `game_id` (uuid, FK)
- `date` (date): 기록 일자
- `rank_playstore` (int): 구글 플레이 매출 순위
- `rank_appstore` (int): 앱스토어 매출 순위
- `est_daily_revenue` (numeric): 국내 추정 일일 매출

### **Table: `kr_community_vibe`**
- `id` (bigint, PK)
- `game_id` (uuid, FK)
- `date` (date)
- `mention_count` (int): 커뮤니티 언급 횟수
- `sentiment_score` (float): 감성 점수 (긍정/부정)

---

## 5. 데이터 분석 예시 (KR Market Use Cases)

### **① 국내 퍼블리셔별 운영 효율 분석**
- **방법**: 넥슨, 카카오게임즈, 호요버스 코리아 등 주요 퍼블리셔별 관리 게임들의 매출 방어력 및 이벤트 주기 효과 비교.

### **② 온/오프라인 이벤트와 매출의 상관관계**
- **가설**: "한국 전용 콜라보 카페나 오프라인 행사 기간에 국내 매출 순위가 유의미하게 상승할 것이다."
- **방법**: 오프라인 행사 일정과 일별 매출 순위 데이터를 시각화하여 상관계수 산출.

### **③ 국내 검색량(화제성)과 매출의 선행 지표 분석**
- **방법**: 네이버 데이터랩의 검색량 증가가 실제 매출 순위 상승의 몇 일 전행 지표가 되는지 타임 시리즈 분석.

### **④ 유저 리뷰 감성 분석을 통한 이탈 징후 파악**
- **방법**: 구글 플레이 리뷰 중 특정 키워드(버그, 운영, 불통 등)의 빈도와 매출 하락세의 연관성 분석.

---

## 6. 실행 로드맵 (KR Focused)

1.  **Phase 1**: 국내 소스(모바일인덱스 등) 대상 크롤러 프로토타입 개발
2.  **Phase 2**: Supabase에 한국 게임 및 시장 지표 테이블 구축
3.  **Phase 3**: 네이버 데이터랩 API 연동 및 일간 검색 데이터 수집 자동화
4.  **Phase 4**: Streamlit 기반 '한국 서브컬쳐 시장 실시간 모니터링 룸' 구축

---

**작성자**: Antigravity (Data Engineering Agent)
**최종 수정일**: 2026-01-08 (한국 시장 집중 수정)

