# ✨ YouTube Intel Collector (Data Harvesting Engine)

## 🎯 프로젝트 개요
YouTube Data API v3를 활용하여 시장 진입 장벽이 낮은 니치 키워드부터 대형 트렌드까지, 실시간 데이터를 수집하고 분석하는 **데이터 엔진**입니다. 단순 조회를 넘어, 콘텐츠의 진정성과 몰입도를 정량화할 수 있는 지표 도출을 목표로 합니다.

## 🚀 주요 기능 (MVP)
- **검색 기반 데이터 수집**: 특정 키워드에 대한 영상 메타데이터(조회수, 게시일, 채널명 등) 자동 수집.
- **카테고리별 데이터 관리**: 주식, 게임, 노래, 흑백요리사 등 관심사별 데이터셋 구축 (CSV).
- **인사이트 리포팅**: 수집된 데이터를 바탕으로 한 확장 분석 전략 제안 (`분석_결과.md`).

## 🛠 기술 스택
- **Language**: Python 3.x
- **API**: YouTube Data API v3
- **Libraries**: `google-api-python-client`, `pandas`, `python-dotenv`
- **Storage**: CSV (Local Data Lake)

## 📋 향후 개발 로드맵 (설계안)
1. **[Phase 1] 데이터 정교화**: 댓글 감성 분석(Sentiment Analysis) 및 참여 지표(Engagement Rate) 계산 로직 추가.
2. **[Phase 2] 실시간 탐지**: 특정 키워드의 조회수 급상승을 감지하는 Viral Alert System 구축.
3. **[Phase 3] AI 최적화**: LLM을 연동하여 상위 노출을 위한 제목 및 SEO 키워드 자동 생성 도구 개발.

## 🎨 설계 철학
- **Data Integrity**: 신뢰할 수 있는 직접 카운트 기반의 데이터 수집.
- **Scalability**: 새로운 키워드와 분석 지표를 즉각적으로 추가할 수 있는 유연한 구조.
- **Actionability**: 분석 데이터가 실제 콘텐츠 제작 전략으로 즉시 전환될 수 있도록 함.
