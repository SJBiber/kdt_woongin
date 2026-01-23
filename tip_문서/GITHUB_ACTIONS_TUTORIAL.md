# GitHub Actions 완벽 가이드

> PC 없이도 매일 자동으로 데이터를 수집하는 방법

---

## 📚 목차

- [초심자용 가이드](#초심자용-가이드)
- [중급자용 가이드](#중급자용-가이드)
- [워크플로우 파일 설명](#워크플로우-파일-설명)
- [문제 해결](#문제-해결)

---

## 초심자용 가이드

> GitHub Actions가 처음이신 분들을 위한 단계별 가이드

### 1단계: GitHub Actions란?

**GitHub Actions**: GitHub에서 제공하는 무료 자동화 서비스
- PC 없이도 코드를 자동 실행
- 매일 정해진 시간에 작업 수행
- 월 2,000분 무료 제공

### 2단계: 필요한 것

1. **GitHub 계정** - 이미 있음 ✓
2. **저장소** - `SJBiber/kdt_woongin` ✓
3. **API 키 4개** - YouTube 2개, Supabase 2개

### 3단계: GitHub Secrets 설정

**Secrets**: 비밀번호처럼 숨겨야 하는 정보를 안전하게 저장하는 곳

#### 설정 방법
1. GitHub 저장소 페이지로 이동
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 버튼 클릭
5. 아래 4개를 하나씩 추가:

| Name | Value | 설명 |
|------|-------|------|
| `YOUTUBE_API_KEY_1` | 첫 번째 YouTube API 키 | YouTube 데이터 조회용 |
| `YOUTUBE_API_KEY_2` | 두 번째 YouTube API 키 | 할당량 초과 시 자동 전환 |
| `SUPABASE_URL` | Supabase 프로젝트 URL | 데이터베이스 주소 |
| `SUPABASE_KEY` | Supabase Service Role Key | 데이터베이스 접근 권한 |

### 4단계: 워크플로우 파일 확인

**워크플로우**: 자동으로 실행할 작업의 설명서

파일 위치: `.github/workflows/collect.yml`
- 이미 생성되어 있음 ✓
- 매일 오전 9시에 자동 실행됨

### 5단계: 수동 테스트

1. GitHub 저장소의 **Actions** 탭 클릭
2. **YouTube 트렌드 자동 수집** 클릭
3. **Run workflow** 버튼 클릭
4. 녹색 **Run workflow** 버튼 다시 클릭
5. 실행 결과 확인 (약 5분 소요)

### 6단계: 자동 실행 확인

- **첫 자동 실행**: 내일 오전 9시
- **확인 방법**: Actions 탭에서 실행 기록 확인
- **실패 시**: 이메일로 알림 받음

---

## 중급자용 가이드

> GitHub Actions 경험이 있는 분들을 위한 심화 가이드

### 워크플로우 구조

```yaml
name: YouTube 트렌드 자동 수집

on:
  schedule:
    - cron: '0 0 * * *'  # UTC 00:00 = KST 09:00
  workflow_dispatch:      # 수동 실행 가능

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - 코드 체크아웃
      - Python 환경 설정
      - 의존성 설치
      - 환경 변수 설정
      - 데이터 수집 실행
```

### 주요 설정 변경

#### 1. 실행 시간 변경
```yaml
schedule:
  - cron: '0 0 * * *'   # 매일 오전 9시 (KST)
  - cron: '0 12 * * *'  # 매일 오후 9시 (KST)
  - cron: '0 */6 * * *' # 6시간마다
```

#### 2. 수집 범위 변경
```yaml
# 전체 기간 (현재 설정)
echo -e "1\ny" | python3 collect.py

# 최근 N일
echo -e "3\n7\ny" | python3 collect.py  # 최근 7일

# 특정 기간
echo -e "2\n2025-12-01\n2026-01-23\ny" | python3 collect.py
```

#### 3. Python 버전 변경
```yaml
- name: Python 설정
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # 3.9, 3.10, 3.12 등으로 변경 가능
```

### 고급 기능

#### 1. 조건부 실행
```yaml
# 평일에만 실행
on:
  schedule:
    - cron: '0 0 * * 1-5'  # 월~금요일만
```

#### 2. 병렬 실행
```yaml
strategy:
  matrix:
    keyword: ['임성근 쉐프', '다른 키워드']
steps:
  - run: python3 collect.py ${{ matrix.keyword }}
```

#### 3. 캐싱으로 속도 향상
```yaml
- name: 의존성 캐시
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

---

## 워크플로우 파일 설명

### 전체 코드
```yaml
name: YouTube 트렌드 자동 수집
# 워크플로우 이름 - Actions 탭에 표시됨

on:
  schedule:
    - cron: '0 0 * * *'
    # Cron 표현식: 분 시 일 월 요일
    # '0 0 * * *' = 매일 UTC 00:00 (KST 09:00)
  
  workflow_dispatch:
  # 수동 실행 버튼 활성화

jobs:
  collect:
    # Job 이름
    runs-on: ubuntu-latest
    # 실행 환경: Ubuntu 최신 버전
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v3
      # GitHub 저장소 코드를 가져옴
    
    - name: Python 설정
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
      # Python 3.11 설치
    
    - name: 의존성 설치
      run: |
        pip install -r youtube_trend_tracker/config/requirements.txt
      # 필요한 Python 패키지 설치
    
    - name: 환경 변수 설정
      run: |
        mkdir -p youtube_trend_tracker/config
        echo "YOUTUBE_API_KEY_1=${{ secrets.YOUTUBE_API_KEY_1 }}" >> youtube_trend_tracker/config/.env
        echo "YOUTUBE_API_KEY_2=${{ secrets.YOUTUBE_API_KEY_2 }}" >> youtube_trend_tracker/config/.env
        echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}" >> youtube_trend_tracker/config/.env
        echo "SUPABASE_KEY=${{ secrets.SUPABASE_KEY }}" >> youtube_trend_tracker/config/.env
      # GitHub Secrets에서 API 키를 가져와 .env 파일 생성
      # ${{ secrets.NAME }} = GitHub Secrets에 저장된 값
    
    - name: 데이터 수집 실행
      run: |
        cd youtube_trend_tracker/scripts
        echo -e "1\ny" | python3 collect.py
      # 수집 스크립트 실행
      # echo -e "1\ny" = 자동 입력 (1: 전체 기간, y: 확인)
```

### 주요 키워드 설명

| 키워드 | 설명 |
|--------|------|
| `name` | 워크플로우 이름 |
| `on` | 실행 조건 (schedule, push, pull_request 등) |
| `schedule` | 정기 실행 설정 |
| `cron` | 실행 시간 (Cron 표현식) |
| `workflow_dispatch` | 수동 실행 버튼 활성화 |
| `jobs` | 실행할 작업 목록 |
| `runs-on` | 실행 환경 (ubuntu, windows, macos) |
| `steps` | 작업 단계 |
| `uses` | 다른 사람이 만든 액션 사용 |
| `run` | 쉘 명령어 실행 |
| `with` | 액션에 전달할 파라미터 |
| `secrets` | GitHub Secrets에 저장된 값 |

---

## 문제 해결

### Q1. 워크플로우가 실행되지 않아요

**확인 사항:**
1. `.github/workflows/collect.yml` 파일이 **저장소 루트**에 있는지 확인
2. YAML 문법 오류가 없는지 확인 (들여쓰기 주의)
3. GitHub Actions가 활성화되어 있는지 확인

**해결 방법:**
```bash
# 파일 위치 확인
ls -la .github/workflows/

# YAML 문법 검사
yamllint .github/workflows/collect.yml
```

### Q2. Secrets를 찾을 수 없다는 오류

**오류 메시지:**
```
Error: Process completed with exit code 1.
ValueError: [!] YOUTUBE_API_KEY_1이 .env 파일에 없습니다.
```

**해결 방법:**
1. Settings → Secrets and variables → Actions 확인
2. 4개 Secret이 모두 등록되어 있는지 확인
3. Secret 이름이 정확한지 확인 (대소문자 구분)

### Q3. API 할당량 초과 오류

**오류 메시지:**
```
[!] 모든 API 키의 할당량이 소진되었습니다.
```

**해결 방법:**
1. 내일까지 기다리기 (할당량은 매일 자정에 리셋)
2. 추가 API 키 발급 후 `YOUTUBE_API_KEY_3` 추가
3. 수집 범위 줄이기 (전체 기간 → 최근 30일)

### Q4. 파일을 찾을 수 없다는 오류

**오류 메시지:**
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory
```

**해결 방법:**
워크플로우 파일의 경로 확인:
```yaml
# 올바른 경로
pip install -r youtube_trend_tracker/config/requirements.txt

# 잘못된 경로
pip install -r config/requirements.txt
```

### Q5. 실행 시간이 너무 오래 걸려요

**원인:**
- 전체 기간 수집 시 약 5~10분 소요 (정상)

**최적화 방법:**
1. 수집 범위 줄이기
2. 캐싱 사용
3. 병렬 처리 (고급)

---

## 💡 유용한 팁

### 1. 로그 확인 방법
- Actions 탭 → 워크플로우 클릭 → 실행 기록 클릭
- 각 단계별 로그 확인 가능
- 오류 발생 시 빨간색으로 표시

### 2. 실행 기록 보관
- 기본 90일 보관
- Settings → Actions → General에서 변경 가능

### 3. 비용 확인
- Settings → Billing → Actions
- 무료 한도: 월 2,000분
- 현재 사용량 확인 가능

### 4. 알림 설정
- Settings → Notifications
- 실패 시 이메일 알림 받기

### 5. 디버깅
```yaml
# 디버그 모드 활성화
- name: 디버그 정보 출력
  run: |
    echo "현재 디렉토리: $(pwd)"
    echo "파일 목록:"
    ls -la
    echo "환경 변수:"
    env | grep YOUTUBE
```

---

## 📚 추가 학습 자료

### 공식 문서
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Cron 표현식 생성기](https://crontab.guru/)
- [YAML 문법 가이드](https://yaml.org/)

### 유용한 액션
- `actions/checkout@v3` - 코드 체크아웃
- `actions/setup-python@v4` - Python 설정
- `actions/cache@v3` - 의존성 캐싱
- `actions/upload-artifact@v4` - 파일 업로드

---

## ✅ 체크리스트

### 초기 설정
- [ ] GitHub Secrets 4개 등록
- [ ] 워크플로우 파일 확인
- [ ] 수동 테스트 실행
- [ ] 실행 결과 확인

### 일일 확인
- [ ] 자동 실행 성공 여부
- [ ] 데이터 수집 완료 확인
- [ ] API 할당량 확인

### 주간 확인
- [ ] 실행 기록 검토
- [ ] 오류 패턴 분석
- [ ] 최적화 필요 여부

---

**작성일**: 2026-01-23
**대상**: 초심자 ~ 중급자
**난이도**: ⭐⭐☆☆☆
