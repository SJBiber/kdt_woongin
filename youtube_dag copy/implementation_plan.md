# 유튜브 크롤링 Airflow DAG 전환 계획

기존 `youtube_crawling` 소스 코드를 Airflow에서 동작할 수 있는 DAG 형태로 변환하여 `kdt_woongin/youtube_dag` 디렉토리에 구성합니다.

## 1. 디렉토리 구조 설정
- `kdt_woongin/youtube_dag/`
    - `youtube_crawling_dag.py`: Airflow DAG 정의 파일
    - `modules/`: 기존 로직을 모듈화하여 저장
        - `__init__.py`
        - `crawler.py`: 유튜브 크롤링 로직 (`YouTubeTrendCrawler` 클래스)
        - `database.py`: DB 저장 로직 (`SupabaseManager` 클래스)
    - `.env`: 환경 변수 (API 키, DB 접속 정보)

## 2. 작업 단계
1. **디렉토리 생성**: `kdt_woongin/youtube_dag` 및 `modules` 폴더 생성
2. **모듈 파일 작성**:
    - `modules/crawler.py`: 기존 `crawler.py`에서 클래스 추출
    - `modules/database.py`: 기존 `database.py`에서 클래스 추출
3. **DAG 파일 작성**:
    - `youtube_crawling_dag.py`: PythonOperator를 사용하여 크롤링 및 저장 작업 정의
    - 매일 정해진 시간에 실행되도록 스케줄링 (예: 매일 오전 0시)
    - Airflow 환경에서 환경 변수를 읽어올 수 있도록 설정 확인
4. **환경 설정 파일 복사**: `.env` 파일을 새 디렉토리에 복사 (또는 Airflow Variable/Connection 권장하지만 우선 파일 기반 유지)

## 3. 주요 변경 사항
- `YouTubeTrendCrawler.get_historical_data`의 기간을 파라미터화하여 필요에 따라 조절 가능하게 함.
- Airflow의 `PythonOperator`를 통해 실행되도록 함수 구조 조정.
- 로그 출력을 Airflow 로그에서 확인할 수 있도록 standard library `logging` 모듈 활용 (선택 사항, 우선 기존 `print` 유지).

## 4. 고려 사항
- Airflow 서버에 필요한 패키지(`google-api-python-client`, `pandas`, `supabase`, `python-dotenv`)가 설치되어 있어야 합니다.
- API 할당량 초과 시의 처리가 DAG 실행 결과(Success/Failure)에 미치는 영향 고려.
