# 수정 히스토리 (Fix History)

---

## 2026-01-27

### 1. Kiwi 사용자 사전 등록 — 복합어/고유명사 분리 방지

- **현상**: Kiwi 형태소 분석기가 `음주운전` → `음주` + `운전`, `흑백요리사` → `흑백` + `요리사`처럼 복합어를 개별 형태소로 분리하여 키워드 의미가 손실됨
- **원인**: Kiwi 기본 사전에 해당 복합어/고유명사가 하나의 단어로 등록되어 있지 않아, 형태소 분석 시 자동으로 분리됨
- **해결**: `Kiwi.add_user_word()` API를 사용하여 사용자 사전에 복합어/고유명사를 등록
- **등록 단어**:
  | 단어 | 품사 태그 | 설명 |
  |------|-----------|------|
  | `음주운전` | NNG (일반명사) | "음주" + "운전" 분리 방지 |
  | `이재명` | NNP (고유명사) | 인명 분리 방지 |
  | `흑백요리사` | NNP (고유명사) | 프로그램명 분리 방지 |
- **수정 내용**:
  1. `USER_DICT` 클래스 변수 추가 — 사용자 사전 단어를 `(단어, 품사태그)` 튜플 리스트로 관리
  2. `__init__`에서 Kiwi 초기화 직후 `add_user_word()` 호출로 사전 등록
  3. 테스트 코드(`__main__`) 업데이트 — 등록된 단어들의 분리 방지 검증용 테스트 케이스 추가
- **대상 파일**: `analyzer/nlp_engine.py`
- **향후 확장**: `USER_DICT` 리스트에 `('새단어', 'NNG')` 형태로 튜플을 추가하면 자동 등록됨

### 2. `nlp_engine.py` 코드 설명 주석 보강
- **변경 내용**: `NLPEngine` 클래스 전체에 상세 설명 주석(docstring, 인라인 주석) 추가
- **목적**: 코드 가독성 향상 및 유지보수 편의를 위한 문서화
- **대상 파일**: `analyzer/nlp_engine.py`

### 3. 백종원 비교분석 — 가설 검증 인사이트로 전면 교체
- **변경 내용**: 기존 "핵심 인사이트" + "권장 대응 전략" 섹션을 제거하고, **4가지 가설 검증 인사이트**로 교체
- **제거된 섹션**:
  - 핵심 인사이트 (논란 성격 비교, 현황 비교, 회복 예측)
  - 권장 대응 전략 (백종원 사례 교훈, 임성근 전략)
- **추가된 가설 검증 4가지**:
  | 가설 | 검증 방법 | 판정 기준 |
  |------|-----------|-----------|
  | 1. 논란 시 관심도 2배 증가 | 논란 전후 일평균 댓글 수 비교 | 1.8배 이상 = 채택 |
  | 2. 분노·실망 댓글 주도 | 논란 후 감정별 비율 계산 | 분노+실망 50% 이상 = 채택 |
  | 3. 1주 후 조롱 증가 | 첫 1주 vs 1주 이후 조롱/분노 비율 비교 | 조롱↑ 분노↓ = 채택 |
  | 4. 1개월 후 관심도 급락 | 주간 댓글 수 추이 (첫주 vs 4주 이후) | 50% 이상 하락 = 채택 |
- **구현 특징**:
  - 각 가설마다 데이터 테이블 + 채택/부분채택/기각 판정 UI
  - 가설 4에 주간 댓글 수 바 차트 포함
  - 하단에 4가지 가설 종합 요약 테이블 표시
  - 데이터 부족 시 "검증 대기" 상태 표시
- **대상 파일**: `pages/2_백종원_비교분석.py`

---

## 2026-01-26

### 1. `2_normalize_baek_jongwon.py` - Supabase Upsert 오류 수정
- **현상**: `2_normalize_baek_jongwon.py` 실행 시 Supabase 400 Bad Request 에러 발생.
  - 에러 메시지: `null value in column "content" of relation "baek_jongwon_youtube_comments" violates not-null constraint`
- **원인**: `baek_jongwon_youtube_comments` 테이블의 `content` 컬럼은 `NOT NULL` 제약 조건이 있으나, 정규화 후 `upsert` 과정에서 `content` 필드를 누락하여 발생. (PostgreSQL의 UPSERT 구문은 INSERT 부분을 먼저 검증하기 때문에 발생)
- **수정**: `updated_data` 생성 시 기존 `row["content"]` 값을 포함하도록 수정.
- **대상 파일**:
  - `Opinion_Analysis/2_normalize_baek_jongwon.py`
  - `Opinion_Analysis/3_local_analysis_baek_jongwon.py`
  - `Opinion_Analysis/4_llm_analysis_baek_jongwon.py`
  - `Opinion_Analysis/2_normalize_text.py` (임성근 예방 차원)
  - `Opinion_Analysis/3_local_analysis.py` (임성근 예방 차원)
  - `Opinion_Analysis/4_llm_analysis.py` (임성근 예방 차원)

### 2. Streamlit 대시보드 초기 에러 수정

#### 2-1. KeyError: 'sentiment_group'
- **원인**: 데이터 전처리 시 `for` 루프 내에서 DataFrame을 수정했지만, Python의 변수 참조 방식으로 인해 원본 DataFrame에 반영되지 않음
- **해결**:
  - 각 DataFrame을 개별적으로 전처리하도록 수정
  - `df_im`과 `df_baek`를 직접 수정하여 컬럼 추가
  - `group_sentiment` 함수를 루프 밖으로 이동하여 재사용
- **대상 파일**:
  - `pages/2_백종원_비교분석.py`
  - `pages/3_시계열_분석.py`
  - `pages/4_상세_통계.py`

#### 2-2. Streamlit 경고: use_container_width
- **원인**: Streamlit 최신 버전에서 `use_container_width=True` 파라미터가 deprecated됨
- **해결**: 모든 `use_container_width=True`를 `width="stretch"`로 변경
- **대상 파일**:
  - `dashboard_main.py`
  - `pages/1_전체_요약.py`
  - `pages/2_백종원_비교분석.py`
  - `pages/3_시계열_분석.py`
  - `pages/4_상세_통계.py`

### 3. Plotly 차트 datetime 관련 에러 수정

#### 3-1. TypeError: unsupported operand type(s) for +: 'int' and 'datetime.date'
- **현상**: `3_시계열_분석.py`에서 `add_vline()` 사용 시 TypeError 발생
- **원인**: `pd.Timestamp().date()` 사용으로 datetime.date 객체 생성, Plotly의 add_vline()이 내부적으로 datetime 연산 수행 시 실패
- **시도한 해결책**:
  1. `.date()` 제거하고 `pd.Timestamp` 직접 사용 → 실패
  2. `datetime(2026, 1, 19)` 사용 → 실패
- **최종 해결**: `add_vline()` 대신 `add_shape()` + `add_annotation()` 조합 사용
- **수정 위치**: `pages/3_시계열_분석.py` 157-173, 185-200줄
- **변경사항**:
  - `dt.date` → `dt.normalize()` (datetime 객체 유지)
  - `add_vline()` → `add_shape(type="line")` + `add_annotation()`

#### 3-2. TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp
- **현상**: 시계열 분석 인사이트 섹션에서 timezone-aware index와 naive Timestamp 비교 시 에러 발생
- **원인**: `daily_im_stats.index`가 timezone-aware이지만 `controversy_date_ts`는 naive Timestamp
- **해결**: timezone 조건부 localization 추가
- **수정 위치**: `pages/3_시계열_분석.py` 367-376줄
```python
if daily_im_stats.index.tz is not None:
    controversy_date_ts = controversy_date_ts.tz_localize('UTC')
```

#### 3-3. NameError: name 'after_avg' is not defined
- **현상**: 변수가 if 블록 내부에서만 정의되어 다른 column에서 참조 시 에러
- **원인**: 변수 스코프 문제 - if 블록 내에서만 정의된 변수를 외부에서 사용
- **해결**: 모든 변수를 if 블록 외부에서 초기화
- **수정 위치**: `pages/3_시계열_분석.py` 338-346줄

### 4. 감정 라벨 한글화
- **변경 내용**: 모든 영어 감정 라벨을 한글로 변경
  - Support → 지지
  - Anger → 분노
  - Neutral → 중립
  - Disappointment → 실망
  - Sarcasm → 조롱
  - Inquiry → 질문
- **대상 파일**: 모든 페이지 파일 (1_전체_요약.py, 2_백종원_비교분석.py, 3_시계열_분석.py, 4_상세_통계.py)
- **수정 방법**: `label_map` 딕셔너리 값 변경

### 5. 시계열 분석 개선

#### 5-1. 의미없는 히트맵 제거
- **현상**: 시간대별 감정 강도 히트맵이 있었으나, 데이터 수집 시 시분초 정보가 없어 의미 없음
- **해결**: 히트맵 섹션 전체 제거 후 **감정별 상세 분석**으로 대체
- **새로운 분석 내용**:
  - 6가지 감정 분류 비율 (가로 막대 차트)
  - 감정별 영향력 (평균 좋아요)
  - 임성근 논란 전후 감정 변화 (stacked bar chart)
- **수정 위치**: `pages/3_시계열_분석.py` 256-357줄

### 6. 데이터 기반 인사이트 추가

#### 6-1. 전체 요약 페이지
- **추가 내용**: 3-column 레이아웃의 핵심 인사이트
  - 여론 변화: 논란 전후 부정 비율 비교, 증가폭
  - 감정 분석: 주요 감정(논란 후), 전체 긍정/부정 비율
  - 대중 공감도: 가장 공감받는 감정, 평균 좋아요
- **수정 위치**: `pages/1_전체_요약.py` 224-295줄

#### 6-2. 백종원 비교분석 페이지
- **추가 내용**: 3-column 레이아웃의 핵심 인사이트
  - 논란의 성격: 백종원(사업적) vs 임성근(개인 범죄)
  - 현황 비교: 논란 전후 수치, 회복률, 임성근 대비
  - 회복 예측: 백종원 실제 회복 데이터 기반 임성근 예측
- **수정 위치**: `pages/2_백종원_비교분석.py` 411-471줄

#### 6-3. 시계열 분석 페이지
- **추가 내용**: 2-column 레이아웃의 트렌드 인사이트
  - 임성근 핵심 트렌드: 논란 전후 평균, 극단값, 관심도
  - 백종원 트렌드 비교: 평균/최고/최저 부정률, 트렌드, 임성근 대비
- **수정 위치**: `pages/3_시계열_분석.py` 335-429줄

#### 6-4. 상세 통계 페이지
- **추가 내용**: 3-column 레이아웃의 상세 통계 인사이트
  - 감정 분포: 가장 많은 감정, 해석
  - 대중 공감: 가장 공감받는 감정, 의미
  - 댓글 특성: 가장 긴 댓글 감정, 분석
- **수정 위치**: `pages/4_상세_통계.py` 372-448줄

### 7. 백종원 비교분석 데이터 로딩 문제 수정

#### 7-1. collection_period 자동 분류 추가
- **현상**: 12월/1월 백종원 데이터가 DB에 있음에도 불구하고 "백종원 현재" 데이터가 비어있음
- **원인**: DB에 `collection_period` 컬럼이 존재하지만 제대로 분류되지 않았거나, 컬럼이 없어서 분류가 안됨
- **1차 수정**:
  - `collection_period` 컬럼이 없을 경우에만 날짜 기반 분류 추가
  - 2-3월: 'controversy', 12월 이후: 'current'
- **디버깅 추가**: 백종원 데이터 정보를 보여주는 expander 추가 (데이터 수, 날짜 범위, collection_period 분포)

#### 7-2. collection_period 분류 기준 변경
- **문제**: 논란 시기(2-3월) 데이터는 있는데 현재 데이터가 여전히 없음
- **원인 분석**: DB에 collection_period 컬럼이 이미 존재하여 if 조건을 통과하지 못하고 재분류가 안됨
- **2차 수정**: if 조건 제거하고 무조건 날짜 기반으로 재분류
- **3차 수정** (사용자 피드백 반영):
  - 논란 시기: 2025년 2-11월 (기존 2-3월에서 확장)
  - 현재: 2025년 12월 이후
- **수정 위치**: `pages/2_백종원_비교분석.py` 105-118줄
- **관련 수정**: 캡션 및 설명 텍스트 업데이트 (186-187, 295-302줄)

### 8. 회복 곡선 예측 개선 및 감정 색상 수정

#### 8-1. 회복 곡선 예측 계수를 실제 데이터 기반으로 계산
- **문제**: 하드코딩된 회복 계수(0.94, 0.82, 0.65 등) 사용
- **개선**: 백종원의 실제 주단위 데이터를 기반으로 회복 패턴 계산
- **구현 방식**:
  - 백종원 데이터를 주단위로 그룹화 (논란 시작일 기준)
  - 0주, 4주(1개월), 12주(3개월), 24주(6개월), 40주(10개월) 데이터 추출
  - 실제 회복률 계산 후 임성근에 적용
- **수정 위치**: `pages/2_백종원_비교분석.py` 293-326줄
- **장점**: 하드코딩 제거 및 실제 데이터 기반 예측

#### 8-2. 감정별 색상 논리적 재배치
- **문제**: Plotly 자동 색상 할당으로 인해 감정과 색상이 일치하지 않음
  - 지지(긍정)가 빨강으로 표시
  - 분노/실망(부정)이 파랑/초록으로 표시
- **해결**: 감정별 고정 색상 맵 정의
  ```python
  emotion_color_map = {
      "지지": "#00CC96",      # 초록 (긍정)
      "분노": "#EF553B",      # 빨강 (강한 부정)
      "중립": "#636EFA",      # 파랑 (중립)
      "실망": "#FFA15A",      # 주황 (부정)
      "조롱": "#AB63FA",      # 보라 (부정)
      "질문": "#B6E880"       # 연두 (기타)
  }
  ```
- **수정 파일**:
  - `pages/1_전체_요약.py`: 6가지 감정 카테고리 차트 (157-167줄)
  - `pages/3_시계열_분석.py`: 감정별 비율 차트 (296-332줄), 논란 전후 비교 (370-402줄)
  - `dashboard_main.py`: 감정 카테고리 설명에 이모지 추가 (54-59줄)
- **적용 방식**:
  - `px.bar`의 `color_discrete_sequence` → `color_discrete_map` 변경
  - `go.Bar`의 `marker_color` 파라미터로 개별 색상 지정
  - 연속 색상 스케일(`color_continuous_scale`) → 이산 색상 맵으로 변경

#### 8-3. 주단위 여론 변화 추이 분석 및 오해 방지
- **현상**: 백종원의 실제 데이터는 악화(57% → 80대%)를 보이나, 대시보드는 "회복 곡선"으로 표시하여 혼란 유발
- **사용자 피드백**: "백종원이 최저가 57이긴한데 최근에는 80대로 올랐는데 벡종원 비교분석 결과에 첨첨 회복한다라고 나와있어서 데이터가 서로 상이한것같은데 ? 회복곡선 예측부분을 주마다 처리하게 해줘"
- **원인**:
  - 하드코딩된 회복 계수가 항상 감소(회복) 가정
  - 실제 주단위 데이터를 확인할 수 없어 트렌드 파악 어려움
- **해결**:
  1. **주단위 데이터 계산** (305-350줄)
     - 논란 시작일(2025-02-01) 기준으로 week 계산
     - `groupby('week_from_controversy')`로 주단위 부정 비율 계산
     - ±2주 moving average로 노이즈 감소
  2. **주단위 추이 시각화** (353-374줄)
     - Expander에 주단위 라인 차트 추가
     - 최저/최고/현재/평균 부정률 통계 표시
     - 사용자가 실제 데이터 확인 가능
  3. **실제 트렌드 감지** (409-420줄)
     - 변화율 계산: `(최종 - 초기) / 초기 * 100`
     - "개선" vs "악화" 자동 판단
     - "회복 곡선 예측" → "여론 변화 예측"으로 용어 변경
  4. **경고 메시지 추가** (302줄)
     - "백종원의 실제 데이터는 회복이 아닌 악화 패턴을 보일 수 있습니다"
- **수정 위치**: `pages/2_백종원_비교분석.py` 291-420줄
- **코드 예시**:
  ```python
  # 주단위 그룹화
  df_baek_full['week_from_controversy'] = ((df_baek_full['published_at'] - controversy_start).dt.days / 7).astype(int)
  weekly_recovery = df_baek_full.groupby('week_from_controversy').apply(
      lambda x: (x['sentiment_group'] == '부정').mean() * 100,
      include_groups=False
  ).reset_index()

  # Moving average (±2주)
  for week in key_weeks:
      week_range = weekly_recovery[
          (weekly_recovery['week'] >= week - 2) &
          (weekly_recovery['week'] <= week + 2)
      ]
      if not week_range.empty:
          baek_recovery.append(week_range['neg_ratio'].mean())

  # 트렌드 감지
  change_rate = ((baek_recovery[-1] - baek_recovery[0]) / baek_recovery[0] * 100)
  trend = "개선" if change_rate < 0 else "악화"
  ```
- **장점**:
  - 실제 데이터 투명성 확보
  - 오해의 소지 제거 (회복/악화 명확히 구분)
  - 주단위 노이즈 감소로 안정적인 패턴 도출

### 9. 시계열 분석 그래프 시각화 개선 (끊김 방지 및 전수 표시)
- **현상**: 이전의 최소 샘플 필터(`NaN` 처리)로 인해 그래프 선이 중간에 끊기는 '이빨 빠짐' 현상 발생 및 원본 데이터 손실 우려.
- **해결**:
  1. **원본 데이터 전수 보존**: 인위적인 `NaN` 처리를 제거하여 데이터가 1개라도 있는 날은 모두 그래프에 표시되도록 복구함.
  2. **가독성 보정 (Connect Gaps)**: 데이터가 아예 없는 날짜 구간도 선이 자연스럽게 이어지도록 Plotly의 `connectgaps=True` 옵션 적용.
  3. **추세선 안정화**: 이동 평균 윈도우를 3일에서 **5일**로 확장하여, 소수 데이터로 인한 스파이크 현상을 억제하고 더 완만한 여론 흐름을 보여줌.
  4. **툴팁 강화**: 마우스 오버 시 해당 날짜의 비율뿐만 아니라 실제 **'댓글 수'**도 함께 표시하여 데이터의 신뢰도를 사용자가 직접 판단할 수 있게 함.
- **대상 파일**: `pages/3_시계열_분석.py`

### 10. YouTube API `publishedBefore` 경계값 오류 수정
- **현상**: 수집 날짜를 `2025-12-26 ~ 2025-12-26`으로 설정했을 때, 12월 27일 영상 1개가 포함되어 저장됨
  - 12월 26일 검색: 37개 발견 → 36개만 저장 (1개가 실제 12/27 업로드)
  - 12월 27일: 원래 40개 + 경계 1개 = 41개 저장
- **원인**: `publishedBefore` 파라미터를 `2025-12-27T00:00:00Z`로 설정하면, 정확히 자정(00:00:00)에 업로드된 영상도 포함됨 (경계값 포함 문제)
- **해결**: `publishedBefore`에서 1초를 빼서 `2025-12-26T23:59:59Z`로 설정
- **수정 위치**: `youtube_trend_tracker/src/tracker_advanced.py` 313-315줄
- **변경 내용**:
  ```python
  # Before:
  day_end_str = datetime.combine(current_date + timedelta(days=1), datetime.min.time()).replace(
      tzinfo=timezone.utc
  ).strftime('%Y-%m-%dT%H:%M:%SZ')

  # After:
  day_end_str = (datetime.combine(current_date + timedelta(days=1), datetime.min.time()).replace(
      tzinfo=timezone.utc
  ) - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
  ```

### 11. 영상 트렌드 대시보드 페이지 신규 생성
- **목적**: `daily_video_trends` 테이블의 수집일별 영상 통계 데이터를 시각화
- **신규 파일**: `pages/5_영상_트렌드.py`
- **데이터 구조**: `daily_video_trends` 테이블 (PK: keyword + upload_date + collected_date)
- **핵심 설계**:
  - 증감/증감률은 DB의 growth 컬럼을 사용하지 않고, **대시보드에서 직접 계산** (`diff()`, `pct_change()`)
  - `collected_date` 기준으로 전체 데이터를 합산하여 일별 총 통계 표시
- **주요 섹션**:
  | 섹션 | 내용 |
  |------|------|
  | KPI 카드 | 최신 수집일 기준 총 영상 수/조회수/좋아요/댓글 + 전일 대비 delta |
  | 수집일별 종합 테이블 | 일자별 합산 통계 + 증감량 + 증감률 |
  | 통계 추이 차트 | 조회수/좋아요/댓글 탭별 Bar + Line 차트 |
  | 증감률 비교 차트 | 조회수/좋아요/댓글 증감률 그룹 Bar 차트 |
- **집계 로직**:
  ```python
  daily_summary = df.groupby('collected_date').agg(
      video_count=('video_count', 'sum'),
      total_views=('total_views', 'sum'),
      total_likes=('total_likes', 'sum'),
      total_comments=('total_comments', 'sum'),
      upload_date_count=('upload_date', 'nunique')
  ).reset_index().sort_values('collected_date')

  daily_summary['views_diff'] = daily_summary['total_views'].diff()
  daily_summary['views_rate'] = daily_summary['total_views'].pct_change() * 100
  ```

### 12. 백종원 비교분석 — 가설 4 영상 트렌드 데이터로 전면 교체
- **변경 전**: 가설 4 "1개월 후 관심도 급락" — 주간 댓글 수 기반 분석
- **변경 후**: 가설 4 "이슈 발생 후 3일간 관심도가 크게 상승한 뒤, 이후 점차 감소할 것이다" — 영상 조회수 증감률 기반 분석
- **데이터 소스 변경**: 댓글 데이터 → `daily_video_trends` 테이블의 조회수 증감률
- **추가 함수**: `load_video_trend_data()` — Supabase에서 영상 트렌드 데이터 로드 및 `collected_date` 기준 합산
- **시각화 변경**:
  - 기존: 주간 댓글 수 바 차트
  - 변경: 조회수 증감률 바 차트 (첫 3일 파란색 강조, 이후 회색)
- **판정 로직 변경**:
  - 첫 3일 평균 증감률 vs 이후 평균 증감률 비교
  - 첫 3일 평균 > 0이고, 이후 평균 < 첫 3일 평균이면 채택
- **대상 파일**: `pages/2_백종원_비교분석.py`

### 13. 시계열 분석 — Timezone 에러 수정 + 분석 대상 고정 표시
- **에러 수정**:
  - **현상**: `TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp` (line 139)
  - **원인**: `date` 컬럼이 timezone-aware (`datetime64[ns, UTC]`)이지만, 필터링 Timestamp는 naive
  - **해결**: `date` 컬럼의 timezone 유무를 동적 확인 후 `tz='UTC'` 적용
  ```python
  if daily_im['date'].dt.tz is not None:
      im_start_date = pd.Timestamp("2025-12-01", tz='UTC')
      im_end_date = pd.Timestamp("2026-01-31", tz='UTC')
  else:
      im_start_date = pd.Timestamp("2025-12-01")
      im_end_date = pd.Timestamp("2026-01-31")
  ```
  - 동일 패턴을 주간 트렌드 필터링에도 적용
- **UI 변경 — 분석 대상 고정 표시**:
  - **제거**: `st.radio("분석 대상 선택", ["임성근", "백종원", "비교"])` 라디오 버튼
  - **제거**: `st.selectbox("분석 대상 선택", ["임성근", "백종원"])` 감정별 분석 selectbox
  - **변경**: 임성근 + 백종원 모두 무조건 순차 표시
  - **영향 범위**: 모든 `if analysis_target in [...]` 조건문 제거
    - 임성근 시계열 분석 → 무조건 표시
    - 백종원 시계열 분석 → `if not df_baek.empty:` 조건만 유지
    - 감정별 상세 분석 → 임성근/백종원 순차 표시 (selectbox 제거)
    - 주간 트렌드 분석 → 무조건 표시 (백종원은 데이터 존재 시)
    - 인사이트 → 무조건 표시
- **대상 파일**: `pages/3_시계열_분석.py` (전면 리팩토링)

---
