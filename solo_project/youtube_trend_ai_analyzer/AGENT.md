# Project Strategy: YouTube Viral Dashboard (YVD)

## 1. Project Overview
YouTube Viral Radar(YVR) Crawler에서 수집하여 DB(Supabase)에 저장된 정제된 트렌드 데이터를 시각화하고 분석하는 전용 대시보드 어플리케이션입니다. 데이터의 수집(Crawling)과 시각화(Visualization)를 분리하여 시스템의 유연성과 유지보수성을 높입니다.

- **프로젝트 명**: `youtube_viral_dashboard`
- **목표**: DB에 축적된 시계열 데이터를 활용해 트렌드 변화를 분석하고 대시보드로 출력

## 2. Tech Stack (Recommended)
- **Frontend/Backend**: Python (Streamlit) 또는 Next.js (Web-based)
  - *추천*: 빠른 개발과 데이터 분석 특화를 위해 **Streamlit** 사용
- **Database**: Supabase (PostgreSQL) - YVR Crawler와 공유
- **Data Analysis**: Pandas, Plotly/Altair

## 3. Key Features
### A. Real-time Trend Monitor
- 현재 시각 기준 가장 강력한 파급력을 가진 상위 키워드 표시
- Power Score 및 Topic Share 실시간 랭킹

### B. Time-series Analysis (History)
- 특정 키워드의 시간대별 Power Score 변화 그래프
- **[핵심] 일별 상위 키워드(1~3위) 다중 바 차트**:
    - 매일의 Top 3 키워드를 선정하고, 각 키워드의 '일별 총 업로드 수'를 다중 바(Grouped Bar) 형태로 시각화하여 트렌드 볼륨 비교
- 일별/주별 급상승 키워드 리포트
- 과거 데이터 조회를 통한 트렌드 주기 분석

### C. Category Insights
- 카테고리별 트렌드 점유율 파이 차트
- 카테고리별 상위 키워드 교차 분석

### D. Alert History Log
- 최근 전송된 바이럴 알림(Surge, High Power) 목록 및 상세 내용 확인

## 4. Architecture Plan
1. **`src/database.py`**: Supabase에서 과거 및 현재 분석 데이터를 효율적으로 읽어오는 Data Access Layer 구현
2. **`src/app.py`**: Streamlit 혹은 Web Framework를 이용한 메인 대시보드 레이아웃 구성
3. **`src/charts.py`**: 시계열 그래프, 바 차트 등 시각화 컴포넌트 모듈화

## 5. Next Steps
- [x] `youtube_viral_dashboard` 디렉토리 생성
- [x] Supabase Read용 API 연동 및 데이터 모델링
- [x] 시계열 분석을 위한 SQL Query 최적화 (Pandas 가공 방식 적용)
- [x] 대시보드 UI/UX 설계 및 구현 (Streamlit 기반)
- [ ] 시각화 고도화 (인터랙티브 분석 기능 추가)

## 6. How to Run
```bash
cd youtube_viral_dashboard
pip install -r requirements.txt
streamlit run app.py
```
