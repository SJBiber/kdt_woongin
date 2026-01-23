# YouTube 트렌드 추적 시스템

## 📊 프로젝트 개요

특정 키워드로 업로드된 YouTube 영상들의 **일별 통계 변화**를 추적하여 **관심도 추이**를 분석하는 시스템입니다.

### 핵심 기능
- ✅ 과거 영상들을 **매일 재조회**하여 증가량 추적
- ✅ **API 키 자동 전환** (할당량 초과 시)
- ✅ 날짜별 집계 데이터의 **증가량/증가율** 계산
- ✅ Supabase 데이터베이스 자동 저장

---

## 🎯 수집 완료 현황

### 전체 통계 (2026-01-23 기준)
- **수집 기간**: 2025-09-01 ~ 2026-01-22 (73일치)
- **총 영상 수**: **1,595개**
- **총 조회수**: **3억 7,242만 회** 🔥
- **평균 조회수/영상**: **23만 3천 회**

---

## 📁 프로젝트 구조

```
youtube_trend_tracker/
├── src/                        # 소스 코드
│   ├── tracker_advanced.py     # API 키 자동 전환 크롤러
│   └── database.py             # DB 관리 클래스
├── scripts/                    # 실행 스크립트
│   ├── collect.py              # 통합 수집 스크립트 ⭐
│   ├── view_data.py            # 데이터 조회
│   └── check_timeline.py       # 시계열 데이터 확인
├── config/                     # 설정 파일
│   ├── .env                    # 환경 변수 (API 키)
│   ├── schema.sql              # 데이터베이스 스키마
│   └── requirements.txt        # 의존성 패키지
├── docs/                       # 문서
│   ├── README.md              # 이 파일
│   ├── PROGRESS.md            # 수집 진행 상황
│   └── QUICKSTART.md          # 빠른 시작 가이드
└── .gitignore                 # Git 제외 파일
```

---

## 🚀 사용 방법

### 1. 환경 설정

#### `config/.env` 파일 생성
```bash
# YouTube API Keys (쿼타 초과 시 자동 전환)
YOUTUBE_API_KEY_1=your_first_api_key
YOUTUBE_API_KEY_2=your_second_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

#### 패키지 설치
```bash
pip install -r config/requirements.txt
```

### 2. 데이터베이스 설정

Supabase SQL Editor에서 `config/schema.sql` 실행

### 3. 데이터 수집

#### 일일 수집 (매일 실행) ⭐
```bash
cd scripts
python3 collect.py
```

대화형 메뉴:
- `1`: 전체 기간 (9/1 ~ 어제)
- `2`: 특정 기간 지정
- `3`: 최근 N일

#### 데이터 확인
```bash
# 전체 데이터 조회
python3 view_data.py

# 특정 업로드 날짜의 시계열 추이
python3 check_timeline.py
```

---

## 📈 데이터 구조

### 테이블: `daily_video_trends`

| 컬럼 | 설명 | 예시 |
|------|------|------|
| `keyword` | 검색 키워드 | "임성근 쉐프" |
| `upload_date` | 영상 업로드 날짜 | 2026-01-19 |
| `collected_date` | 데이터 수집 날짜 | 2026-01-23 |
| `video_count` | 영상 개수 | 142 |
| `total_views` | 총 조회수 | 2,526,879 |
| `total_comments` | 총 댓글 | 3,777 |
| `total_likes` | 총 좋아요 | 19,402 |
| `views_growth` | 조회수 증가량 | +50,000 |
| `views_growth_rate` | 조회수 증가율 (%) | +2.5 |

**기본 키**: `(keyword, upload_date, collected_date)`

---

## 🔧 주요 기능

### 1. API 키 자동 전환
- `config/.env`에 여러 API 키 설정 가능
- 할당량 초과 시 자동으로 다음 키로 전환
- 모든 키 소진 시 안전하게 중단

### 2. 증가량 자동 계산
- 전날 수집 데이터와 비교하여 자동 계산
- 증가량 (절대값) + 증가율 (%) 모두 저장

### 3. 시계열 추적
- 같은 업로드 날짜의 영상을 매일 재조회
- 시간에 따른 관심도 변화 추적

---

## 📊 활용 예시

### SQL 쿼리

#### 특정 업로드 날짜의 추이
```sql
SELECT collected_date, total_views, views_growth, views_growth_rate
FROM daily_video_trends
WHERE keyword = '임성근 쉐프' AND upload_date = '2026-01-19'
ORDER BY collected_date;
```

#### 최신 트렌드 조회
```sql
SELECT upload_date, total_views, views_growth_rate
FROM daily_video_trends
WHERE keyword = '임성근 쉐프' AND collected_date = CURRENT_DATE
ORDER BY upload_date DESC
LIMIT 30;
```

---

## 🔄 자동화

### Cron (Linux/Mac)
```bash
# 매일 오전 9시 실행
0 9 * * * cd /path/to/youtube_trend_tracker/scripts && python3 collect.py
```

### Windows 작업 스케줄러
1. 작업 스케줄러 열기
2. 새 작업 만들기
3. 트리거: 매일 오전 9시
4. 동작: `python collect.py` 실행 (scripts 디렉토리에서)

---

## ⚠️ 주의사항

- YouTube API 일일 한도: 10,000 유닛
- 여러 API 키 사용 권장 (2개 이상)
- 매일 수집하여 증가량 데이터 축적

---

## 📄 라이선스

MIT License

---

## 👤 작성자

배승재 (Bae Seungjae)

---

## 📅 업데이트 이력

- **2026-01-23**: 디렉토리 구조 정리, API 키 자동 전환 기능 추가
- **2026-01-22**: 초기 버전 생성
