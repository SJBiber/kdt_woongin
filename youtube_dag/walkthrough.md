# 유튜브 트렌드 크롤링 DAG 사용 안내 (Airflow 최적화 버전)

이 DAG는 Airflow의 **Variable**과 **Connection** 기능을 활용하여 보안과 유연성을 높였습니다.

## 1. 사전 설정 사항

### A. Airflow Variable 설정
Airflow UI (`Admin` -> `Variables`)에서 다음 변수를 추가해야 합니다.
- **Key**: `YOUTUBE_API_KEY`
- **Value**: 유튜브 데이터 API 키 값

### B. Airflow Connection 설정
Airflow UI (`Admin` -> `Connections`)에서 Supabase DB 연결 정보를 추가해야 합니다.
- **Connection Id**: `supabase_conn`
- **Connection Type**: `Postgres`
- **Host**: Supabase Host (예: `aws-0-ap-northeast-2.pooler.supabase.com`)
- **Schema**: `postgres`
- **Login**: `postgres.{project_ref}`
- **Password**: DB 비밀번호
- **Port**: `5432` 또는 `6543` 

### C. Airflow Email (SMTP) 설정
이메일 발송을 위해서는 Airflow 서버(`airflow.cfg`) 또는 환경 변수에 SMTP 설정이 되어 있어야 합니다. (G메일 기준 예시)
- `AIRFLOW__SMTP__SMTP_HOST`: `smtp.gmail.com`
- `AIRFLOW__SMTP__SMTP_STARTTLS`: `True`
- `AIRFLOW__SMTP__SMTP_SSL`: `False`
- `AIRFLOW__SMTP__SMTP_USER`: `본인의 G메일 주소`
- `AIRFLOW__SMTP__SMTP_PASSWORD`: `G메일 앱 비밀번호 (16자리)`
- `AIRFLOW__SMTP__SMTP_PORT`: `587`
- `AIRFLOW__SMTP__SMTP_MAIL_FROM`: `본인의 G메일 주소`

### D. 수신 이메일 Variable 설정 (다중 수신 가능)
- **Key**: `RECEIVER_EMAILS`
- **Value**: `email1@gmail.com, email2@gmail.com` (쉼표로 구분하여 여러 명 등록 가능)

## 2. 주요 변경 사항
- **직접 쿼리 실행**: `Supabase` 라이브러리 대신 Airflow의 `PostgresHook`을 사용하여 SQL `INSERT ... ON CONFLICT` 쿼리를 직접 전송합니다.
- **성공 알림**: 작업 완료 후 `EmailOperator`를 통해 지정된 메일로 작업 결과를 전송합니다.
- **보안 강화**: `.env` 파일 대신 Airflow 내장 관리 기능을 사용하여 인증 정보를 안전하게 보호합니다.

## 3. 설치 패키지
Airflow 환경에 다음 라이브러리가 설치되어 있어야 합니다.
```bash
pip install google-api-python-client pandas apache-airflow-providers-postgres
```

## 4. 파일 구성
- `youtube_crawling_dag.py`: 메인 DAG 정의.
- `modules/crawler.py`: `Variable.get()`을 사용한 유튜브 수집 로직.
- `modules/database.py`: `PostgresHook`을 사용한 SQL 실행 로직.
