# 📊 YouTube Insights Dashboard (Visualization Suite)

## 🎯 프로젝트 개요
`YouTube Intel Collector`로부터 수집된 원천 데이터를 시각적으로 재구성하여, 사용자가 한눈에 트렌드를 파악하고 세부 데이터에 접근할 수 있도록 하는 **직관적인 시각화 도구**입니다.

## 🚀 주요 기능 (MVP)
### 1. 📈 Interactive Dashboard (`dashboard.py`)
- **트렌드 시각화**: 날짜별 총 조회수 추이를 바 그래프로 시각화하여 인기 급상승 구간을 즉시 파악.
- **포맷팅 최적화**: 큰 숫자를 가독성 있게 표현 (예: 1.0M, 50.2K) 및 마우스 오버 시 상세 정보 제공.
- **동적 로드**: 로컬의 다양한 분석 데이터셋(CSV)을 자유롭게 로드하여 즉시 분석 가능.

### 2. 🔍 Data Audit Viewer (`viewer.py`)
- **스마트 필터링**: 영상 제목 내 키워드 실시간 필터링 기능 제공.
- **정렬 시스템**: 조회수, 등록일 등 주요 지표 기준 오름차순/내림차순 정렬.
- **One-Click 이동**: 데이터 행 더블 클릭 시 브라우저를 통해 실제 영상으로 즉시 랜딩.

## 🛠 기술 스택
- **Language**: Python 3.x
- **GUI Framework**: Tkinter
- **Visualization**: Matplotlib
- **Data Engineering**: Pandas

## 📋 향후 개발 로드맵 (설계안)
1. **[Phase 1] UI/UX 고도화**: Tkinter 커스텀 테마 적용 및 다크 모드 지원.
2. **[Phase 2] 복합 분석 차트**: 단순 조회수 외에 참여율(Engagement) 분산 차트 등 고도화된 시각화 추가.
3. **[Phase 3] 웹 대시보드 전환**: Streamlit 또는 React 기반의 웹 인터페이스로 확장 고려.

## 🎨 설계 및 디자인 철학
- **Visual Excellence**: 전문적인 데이터 분석 도구 느낌의 깔끔하고 정제된 레이아웃.
- **User-Centric**: 복잡한 명령어가 아닌 클릭과 검색 위주의 직관적인 인터랙션 제공.
- **Real-time Feedback**: 데이터 필터링 및 차트 갱신 시 지연 없는 사용자 경험 구현.
