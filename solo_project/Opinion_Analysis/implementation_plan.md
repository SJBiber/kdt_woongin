# 구현 계획: 유튜브 정밀 여론 분석 시스템 (분리형 파이프라인 구조)

이 프로젝트는 대중적인 유튜버의 특정 사건 전후 여론 변화를 정밀하게 추적하기 위해 수집, 정제, 분석 과정을 독립적인 프로그램으로 분리하여 효율성을 극대화한 시스템입니다.

## 1. 전용 프로그램 구조 (4-Step Pipeline)
데이터 분석의 병목 현상을 해결하기 위해 공정을 4단계로 분리하였습니다.

1.  **`1_collect_data.py`**: 유튜브 URL(`youtube_link.txt`)을 순회하며 원본 댓글 수집 및 DB 저장.
2.  **`2_normalize_text.py`**: 수집된 원본 텍스트에 대해 특수문자 제거 및 키워드 추출 수행 (**초고속 처리**).
3.  **`3_local_analysis.py`**: 정규화된 텍스트 기반으로 빠르게 로컬 BERT(KoELECTRA) 감성 분석 수행 (라벨링 가이드 적용).
4.  **`4_llm_analysis.py`**: DeepSeek-V3 LLM을 활용하여 날짜 맥락이 포함된 최종 정밀 감정 라벨링 단계 (API 기반).

## 2. 주요 분석 파이프라인
*   **수집 (Collection)**: `youtube-comment-downloader` 기반 멀티 쓰레드 지향 수집.
*   **정제 (Normalization)**: 
    *   **특수문자 제거**: 정규표현식 기반 고속 처리
    *   **키워드 추출**: SoyNLP LTokenizer + 150개+ 불용어 필터링
    *   **성능**: 50개당 0.3초 (초고속 처리)
    *   **옵션**: ET5 맞춤법 교정 (필요 시 활성화 가능, 배치 처리 지원)
*   **하이브리드 분석 (Hybrid)**: 
    *   **Local BERT**: 6종 감정(Support, Anger, Neutral, Disappointment, Sarcasm, Inquiry) 1차 분류.
    *   **DeepSeek LLM**: 1월 19일 사건 전후 날짜 맥락을 고려하여 '비꼼(Sarcasm)'과 '진심'을 최종 판별.
*   **시각화 (Visualization)**: Streamlit 대시보드를 통해 인사이트 제공.

## 3. 핵심 모듈 상세
*   **Corrector**: `analyzer/corrector.py` (ET5 기반, 배치 처리 + GPU 지원)
*   **NLP Engine**: `analyzer/nlp_engine.py` (SoyNLP 기반, 150+ 불용어)
*   **Sentiment**: `analyzer/sentiment_analyzer.py` (KoELECTRA 기반)
*   **LLM Analyzer**: `analyzer/deepseek_analyzer.py` (DeepSeek-V3 기반)

## 4. 성능 최적화 (2026-01-22 적용)
### Phase 2 텍스트 정규화 최적화
- **배치 처리**: 50개 단위 처리 (8GB 메모리 최적화)
- **맞춤법 교정**: 비활성화 (속도 우선, 필요 시 재활성화)
- **불용어 확장**: 30개 → 150개+ (품질 향상)
- **성능 개선**: 233배 속도 향상 (70초 → 0.3초/50개)
- **처리량**: 시간당 약 600,000개 댓글 처리 가능

## 5. 데이터베이스 및 기술 스택
- **Database**: Supabase (PostgreSQL)
- **NLP**: KoELECTRA, ET5 (옵션), SoyNLP
- **LLM**: DeepSeek API
- **UI**: Streamlit

