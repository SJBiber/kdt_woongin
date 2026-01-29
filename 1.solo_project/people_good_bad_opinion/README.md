# 백종원 vs 임성근 여론 비교 분석 프로젝트

## 프로젝트 개요

임성근 쉐프의 논란(2026년 1월)과 백종원의 역대 최악 논란(2025년 2-3월)을 비교 분석하여:
1. 논란 발생 시 부정적 여론의 증가율 분석
2. 여론이 과열되고 식어가는 주기(관심도 소강 상태) 파악
3. 영상 관심지수 추이 분석

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **언어** | Python 3.9+ |
| **형태소 분석** | Kiwi (kiwipiepy) - 500+ 불용어, 사용자 사전 등록 |
| **감성 분석 (LLM)** | DeepSeek-V3 (OpenAI SDK 호환, 배치 20개) |
| **데이터베이스** | Supabase (PostgreSQL) |
| **대시보드** | Streamlit + Plotly |
| **영상 추적** | YouTube Data API v3 |
| **자동화** | GitHub Actions |

---

## 프로젝트 구조

```
people_good_bad_opinion/
├── Opinion_Analysis/                     # 데이터 수집, 분석, 대시보드
│   ├── 1_collect_data.py                # 임성근 댓글 수집
│   ├── 1_collect_baek_jongwon.py        # 백종원 댓글 수집
│   ├── 2_normalize_text.py              # 임성근 텍스트 정규화 (Kiwi 기반)
│   ├── 2_normalize_baek_jongwon.py      # 백종원 텍스트 정규화 (Kiwi 기반)
│   ├── 3_local_analysis.py              # 임성근 BERT 분석
│   ├── 3_local_analysis_baek_jongwon.py # 백종원 BERT 분석
│   ├── 4_llm_analysis.py               # 임성근 LLM 분석
│   ├── 4_llm_analysis_baek_jongwon.py   # 백종원 LLM 분석
│   ├── dashboard_main.py               # Streamlit 대시보드 메인
│   ├── pages/
│   │   ├── 1_전체_요약.py               # 임성근 여론 전체 요약
│   │   ├── 2_감성_비교분석.py            # 백종원 vs 임성근 + 가설 검증
│   │   ├── 3_추이_비교분석.py            # 시계열 분석 + 주간 트렌드
│   │   ├── 4_상세_통계.py               # 감정별 상세 통계
│   │   └── 5_영상_트렌드.py             # 관심지수 분석
│   ├── analyzer/
│   │   ├── nlp_engine.py               # Kiwi 기반 NLP (500+ 불용어, 사용자 사전)
│   │   ├── sentiment_analyzer.py       # KoELECTRA BERT 감성 분석
│   │   ├── deepseek_analyzer.py        # 임성근 DeepSeek LLM 분석기
│   │   ├── deepseek_baek_jongwon_analyzer.py # 백종원 DeepSeek LLM 분석기
│   │   ├── corrector.py                # ET5 맞춤법 교정 (비활성화)
│   │   └── stat_analyzer.py            # 통계 분석 엔진
│   ├── collector/
│   │   ├── youtube_collector.py        # YouTube 댓글 수집기
│   │   └── community_collector.py      # 커뮤니티 게시글 수집기
│   ├── database/
│   │   ├── supabase_client.py          # Supabase 클라이언트
│   │   ├── schema.sql                  # 임성근 테이블
│   │   └── baek_jongwon_schema.sql     # 백종원 테이블
│   └── utils/
│       └── logger.py                   # 로깅 유틸리티
│
├── youtube_trend_tracker/               # 영상 관심도 추적 시스템
│   ├── src/                            # 소스 코드 (tracker_advanced.py, database.py)
│   ├── scripts/                        # 실행 스크립트 (collect.py, view_data.py)
│   ├── config/                         # 설정 파일 (.env, schema.sql, requirements.txt)
│   └── docs/                           # 문서
│
├── README.md                           # 이 파일
├── PLAN.md                             # PPT 제작 계획
├── dashbord.md                         # 대시보드 요구사항 (초기)
├── 전문가_조언_및_개선계획서.md          # 프로젝트 전체 계획
├── 백종원_데이터_수집_가이드.md          # 백종원 데이터 수집 가이드
└── 최종_검증_체크리스트.md              # 검증 체크리스트
```

---

## 6가지 감정 카테고리 (0-5)

| 코드 | 영문 | 한글 | 색상 | 분류 |
|------|------|------|------|------|
| 0 | support | 지지 | #00CC96 (초록) | 긍정 |
| 1 | anger | 분노 | #EF553B (빨강) | **부정** |
| 2 | neutral | 중립 | #636EFA (파랑) | 그외 |
| 3 | disappointment | 실망 | #FFA15A (주황) | **부정** |
| 4 | sarcasm | 조롱 | #AB63FA (보라) | **부정** |
| 5 | inquiry | 질문 | #B6E880 (연두) | 그외 |

**부정적 감정** = 1(분노) + 3(실망) + 4(조롱)

---

## 3단계 분리형 파이프라인

```
[Step 1] 수집        → 1_collect_data.py / 1_collect_baek_jongwon.py
[Step 2] 텍스트 정규화 → 2_normalize_text.py (Kiwi 형태소 분석, 500+ 불용어)
[Step 3] LLM 분석     → 4_llm_analysis.py (DeepSeek-V3 정밀 감정 판별)
```

---

## 대시보드 구성 (5페이지)

### 1. 전체 요약
- 임성근 여론 핵심 KPI (부정 비율, 감정 강도)
- 감정 그룹 분포 (긍정/부정/그외)
- 논란 전후 비교 (1월 19일 기준)
- 6가지 감정 카테고리 분포 + 워드클라우드

### 2. 감성 비교분석 (vs 백종원)
- 핵심 지표 비교 (임성근 현재 vs 백종원 논란시 vs 백종원 현재)
- **4가지 가설 검증**:
  1. 논란 시 관심도 2배 증가
  2. 분노/실망 댓글이 주도
  3. 1주 후 조롱 비율 증가
  4. 이슈 발생 후 관심도 점차 감소
- 주단위 여론 변화 추이

### 3. 추이 비교분석
- 날짜별 감정 변화 라인 차트
- 일별 댓글 수 추이 (관심도)
- 감정별 상세 분석 (비율, 영향력, 논란 전후 변화)
- 주간 트렌드 분석

### 4. 상세 통계
- 감정별 상세 통계 테이블
- 영향력 분석 (좋아요 Top 10 댓글)
- 가중 평균 감성 점수
- 데이터 필터링 및 CSV 다운로드

### 5. 영상 트렌드 (관심지수)
- KPI 카드 (조회수/좋아요/댓글 + 전일 대비 delta)
- 수집일별 종합 통계 테이블
- 통계 추이 차트 (조회수/좋아요/댓글 탭별)
- 증감률 비교 차트

---

## 실행 방법

### 데이터 분석 파이프라인
```bash
cd Opinion_Analysis

# 댓글 수집
python3 1_collect_data.py              # 임성근
python3 1_collect_baek_jongwon.py --period controversy --limit 500  # 백종원 논란시
python3 1_collect_baek_jongwon.py --period current --limit 500      # 백종원 현재

# 텍스트 정규화 (Kiwi 기반)
python3 2_normalize_text.py
python3 2_normalize_baek_jongwon.py

# BERT 감성 분석
python3 3_local_analysis.py
python3 3_local_analysis_baek_jongwon.py

# LLM 정밀 분석
python3 4_llm_analysis.py
python3 4_llm_analysis_baek_jongwon.py
```

### 대시보드 실행
```bash
cd Opinion_Analysis
streamlit run dashboard_main.py
# http://localhost:8501 에서 확인
```

### 영상 트렌드 수집
```bash
cd youtube_trend_tracker/scripts
python3 collect.py
```

---

## 데이터베이스 스키마

### 임성근 테이블: `im_sung_gen_youtube_comments`
| 컬럼 | 타입 | 설명 |
|------|------|------|
| comment_id | TEXT (PK) | 댓글 고유 ID |
| video_id | TEXT | 영상 ID |
| content | TEXT | 원본 텍스트 |
| keywords | TEXT[] | Kiwi 추출 키워드 |
| sentiment_label | INTEGER | BERT 감정 (0-5) |
| sentiment_score | FLOAT | BERT 신뢰도 |
| llm_sentiment | INTEGER | DeepSeek 감정 (0-5) |
| published_at | TIMESTAMP | 작성 시각 |
| collected_date | DATE | 수집 날짜 |

### 백종원 테이블: `baek_jongwon_youtube_comments`
임성근 테이블과 동일 구조 + `collection_period` ('controversy' or 'current'), `target_person` ('백종원')

### 영상 트렌드 테이블: `daily_video_trends`
| 컬럼 | 타입 | 설명 |
|------|------|------|
| keyword | TEXT | 검색 키워드 |
| upload_date | DATE | 영상 업로드 날짜 |
| collected_date | DATE | 데이터 수집 날짜 |
| video_count | INTEGER | 영상 수 |
| total_views | BIGINT | 총 조회수 |
| total_likes | INTEGER | 총 좋아요 |
| total_comments | INTEGER | 총 댓글 수 |
| views_growth | BIGINT | 조회수 증가량 |
| views_growth_rate | FLOAT | 조회수 증가율 (%) |

---

## 참고 문서

| 문서 | 설명 |
|------|------|
| `Opinion_Analysis/ai_prompt.md` | AI 협업 마스터 프롬프트 |
| `Opinion_Analysis/fix_history.md` | 수정 이력 |
| `Opinion_Analysis/설계서.md` | 시스템 설계서 |
| `Opinion_Analysis/implementation_plan.md` | 구현 계획 |
| `전문가_조언_및_개선계획서.md` | 전체 프로젝트 계획 |
| `백종원_데이터_수집_가이드.md` | 백종원 데이터 수집 가이드 |
| `최종_검증_체크리스트.md` | 검증 체크리스트 |

---

## 진행 상황

1. ✅ 임성근 데이터 수집 및 전체 분석 완료 (약 31,500개 댓글)
2. ✅ 백종원 데이터 수집 및 전체 분석 완료 (약 13,900개 댓글)
3. ✅ 5페이지 Streamlit 대시보드 구축 완료
4. ✅ 4가지 가설 검증 기반 비교 분석 완료
5. ✅ 영상 트렌드 추적 시스템 구축 (GitHub Actions 자동화)
6. ✅ 주단위 여론 변화 추이 및 소강 주기 분석 완료
7. ✅ 최종 발표 자료 작성
