# 자동화 설정 가이드

## 🎯 자동화 방법 선택

### ✅ 추천: macOS Cron (간단하고 충분)
- 이미 설치되어 있음
- 설정 1분이면 완료
- 매일 같은 시간에 실행하기 완벽

### ❌ 불필요: Airflow, n8n
- 우리 작업에는 과함 (단순히 매일 1번 스크립트 실행)
- 설치/설정 복잡
- 리소스 낭비

---

## 🚀 Cron 자동화 설정 (5분 완료)

### 1단계: Cron 편집기 열기

```bash
crontab -e
```

처음 실행하면 편집기를 선택하라고 나옵니다. `vim` 또는 `nano` 선택하세요.

### 2단계: Cron 작업 추가

편집기에 다음 줄을 추가:

```bash
# YouTube 트렌드 자동 수집 (매일 오전 9시)
0 9 * * * /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker/scripts/auto_collect.sh
```

**설명**:
- `0 9 * * *`: 매일 오전 9시 0분
- 뒤의 경로: 실행할 스크립트

### 3단계: 저장 및 종료

- **vim**: `:wq` 입력 후 Enter
- **nano**: `Ctrl+X` → `Y` → Enter

### 4단계: Cron 작업 확인

```bash
crontab -l
```

방금 추가한 작업이 보이면 성공!

---

## 🕐 Cron 시간 설정 변경

다른 시간에 실행하고 싶다면:

```bash
# 형식: 분 시 일 월 요일
0 9 * * *    # 매일 오전 9시
0 21 * * *   # 매일 오후 9시
0 */6 * * *  # 6시간마다
0 9 * * 1    # 매주 월요일 오전 9시
```

---

## 📋 로그 확인

자동 수집 로그는 다음 위치에 저장됩니다:

```bash
# 오늘 로그 확인
cat /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker/logs/collect_$(date +%Y%m%d).log

# 최근 로그 확인
ls -lt /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker/logs/
```

---

## 🧪 수동 테스트

Cron 설정 전에 스크립트가 잘 작동하는지 테스트:

```bash
cd /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker/scripts
./auto_collect.sh
```

로그 파일이 생성되고 데이터가 수집되면 성공!

---

## ⚠️ 문제 해결

### Cron이 실행되지 않는 경우

1. **권한 확인**
   ```bash
   ls -l /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker/scripts/auto_collect.sh
   ```
   `-rwxr-xr-x`로 시작해야 함 (실행 권한)

2. **Python 경로 확인**
   ```bash
   which python3
   ```
   스크립트에서 올바른 경로 사용 중인지 확인

3. **로그 확인**
   ```bash
   # macOS 시스템 로그
   log show --predicate 'process == "cron"' --last 1h
   ```

---

## 🔄 Cron 작업 관리

### 모든 Cron 작업 보기
```bash
crontab -l
```

### Cron 작업 편집
```bash
crontab -e
```

### 모든 Cron 작업 삭제
```bash
crontab -r
```

---

## 💡 추가 옵션

### 실행 결과를 이메일로 받기

macOS에서 메일 설정이 되어 있다면:

```bash
MAILTO=your@email.com
0 9 * * * /path/to/auto_collect.sh
```

### 여러 시간대에 실행

```bash
# 오전 9시와 오후 9시에 실행
0 9,21 * * * /path/to/auto_collect.sh
```

---

## ✅ 완료 체크리스트

- [ ] `auto_collect.sh` 실행 권한 확인
- [ ] 수동으로 스크립트 테스트
- [ ] Cron 작업 추가
- [ ] `crontab -l`로 확인
- [ ] 내일 오전 9시에 로그 확인

---

**설정 완료 후 내일 오전 9시에 자동으로 데이터가 수집됩니다!** 🎉
