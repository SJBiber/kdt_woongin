# 여론 분석 프로젝트: AI 어시스턴트 협업 프롬프트 가이드

이 문서는 **임성근 vs 백종원 여론 비교 분석 프로젝트**의 현재 상태를 요약하고, 이후 AI와 효율적으로 협업하기 위한 마스터 프롬프트를 담고 있습니다.

## 프로필 및 프로젝트 배경
*   **분석 대상**: 임성근 셰프(2026년 1월 논란) vs 백종원(2025년 2-3월 논란) 여론 비교 분석
*   **기술 스택**: Python, Supabase (PostgreSQL), BERT (KoELECTRA), DeepSeek LLM (OpenAI SDK), **Kiwi (kiwipiepy)**, Streamlit, Plotly
*   **데이터 스키마**:
    *   `im_sung_gen_youtube_comments` 테이블 (임성근)
    *   `baek_jongwon_youtube_comments` 테이블 (백종원)
    *   `daily_video_trends` 테이블 (영상 트렌드)
    *   `sentiment_label` (BERT): 0-5 (6가지 감정 카테고리)
    *   `llm_sentiment` (DeepSeek): 0-5 (6가지 감정 카테고리)
    *   `keywords`: Kiwi 형태소 분석 기반 명사 리스트

---

## AI에게 지시할 때 사용하는 [마스터 프롬프트]

이후 새로운 AI 세션을 시작하거나 추가 기능을 구현할 때 아래 내용을 복사해서 입력하세요.

> **[Prompt Start]**
> 너는 **유튜브 댓글 여론 분석 프로젝트**의 전문 개발자이자 분석가야. 현재 프로젝트 상황은 다음과 같아:
>
> 1. **감성 분석 구조**: BERT(로컬)와 DeepSeek(API)를 병행하여 **6가지 감정 카테고리(0-5)**로 분석함.
>    - 0: support (응원, 지지, 복귀 기대)
>    - 1: anger (분노, 욕설, 강한 적대감)
>    - 2: neutral (중립, 무의미한 나열)
>    - 3: disappointment (실망, 유감, 팬이었으나 돌아섬)
>    - 4: sarcasm (조롱, 비꼼, 반어법)
>    - 5: inquiry (질문, 정보 요청, 유저 간 분쟁)
>    - **부정적 감정** = 1 + 3 + 4 (anger + disappointment + sarcasm)
> 2. **DeepSeek 최적화**: 비용 및 속도 절감을 위해 20개씩 '배치(Batch)'로 묶어서 분석하며, 결과는 JSON 정수 배열로 받음.
> 3. **텍스트 전처리**: **Kiwi (kiwipiepy)** 형태소 분석기 기반으로 키워드 추출. 500개+ 불용어 필터링. 사용자 사전으로 복합어(음주운전, 흑백요리사 등) 분리 방지.
> 4. **DB 처리**: Supabase를 사용하며, 중복 방지를 위해 `comment_id` 기준 Upsert를 수행함.
> 5. **비교 분석**: 임성근(현재) vs 백종원(논란시) vs 백종원(현재) 3개 시점 비교. 4가지 가설 검증 기반 분석.
> 6. **대시보드**: Streamlit 5페이지 구성 (전체요약, 감성비교분석, 추이비교분석, 상세통계, 영상트렌드)
>
> 이 맥락을 바탕으로 내 질문에 답변해줘.
> **[Prompt End]**

---

## 핵심 파일 및 역할

### 4단계 분리형 파이프라인
*   `1_collect_data.py` / `1_collect_baek_jongwon.py`: 유튜브 댓글 수집 및 DB 저장
*   `2_normalize_text.py` / `2_normalize_baek_jongwon.py`: Kiwi 형태소 분석 기반 키워드 추출
*   `3_local_analysis.py` / `3_local_analysis_baek_jongwon.py`: KoELECTRA BERT 감성 분석
*   `4_llm_analysis.py` / `4_llm_analysis_baek_jongwon.py`: DeepSeek LLM 정밀 감정 분석

### 핵심 모듈
*   `analyzer/nlp_engine.py`: Kiwi 기반 텍스트 전처리 및 키워드 추출 (500+ 불용어, 사용자 사전)
*   `analyzer/deepseek_analyzer.py`: 임성근 전용 DeepSeek LLM 분석기
*   `analyzer/deepseek_baek_jongwon_analyzer.py`: 백종원 전용 DeepSeek LLM 분석기
*   `analyzer/sentiment_analyzer.py`: KoELECTRA 기반 로컬 BERT 분석기
*   `analyzer/corrector.py`: ET5 기반 맞춤법 교정 (비활성화 상태, 필요 시 활성화)
*   `analyzer/stat_analyzer.py`: 감성 점수 가중치 기반 통계 분석 엔진

### 대시보드
*   `dashboard_main.py`: 메인 홈 페이지
*   `pages/1_전체_요약.py`: 임성근 여론 전체 요약
*   `pages/2_감성_비교분석.py`: 백종원 vs 임성근 감성 비교 + 4가지 가설 검증
*   `pages/3_추이_비교분석.py`: 시계열 분석 및 주간 트렌드
*   `pages/4_상세_통계.py`: 감정별 상세 통계 및 데이터 탐색
*   `pages/5_영상_트렌드.py`: 조회수/좋아요 기반 관심지수 분석

### 데이터베이스
*   `database/supabase_client.py`: Supabase 클라이언트 (임성근 + 백종원 메서드)
*   `database/schema.sql`: 임성근 테이블 스키마
*   `database/baek_jongwon_schema.sql`: 백종원 테이블 스키마

---

## 팁
*   **비용 절감**: DeepSeek 분석 시 반드시 `analyze_batch` 기능을 사용하여 한 번에 20개씩 처리하도록 유지하세요.
*   **무결성 유지**: DB 컬럼이 `INTEGER` 타입이므로, 코드에서 숫자로 결과를 내보내는지 항상 확인하세요.
*   **분석 고도화**: 특정 키워드(예: "음주운전")에 대한 여론만 따로 보고 싶을 때는 `keywords` 필드를 활용해 필터링을 요청하세요.
*   **사용자 사전**: 새로운 복합어가 분리되는 경우 `nlp_engine.py`의 `USER_DICT`에 `('새단어', 'NNG')` 형태로 추가하세요.
