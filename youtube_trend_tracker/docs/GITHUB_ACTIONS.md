# GitHub Actions 자동화 설정 가이드

## 🎯 왜 GitHub Actions?

- ✅ **완전 무료** (월 2,000분 제공)
- ✅ **PC 꺼도 됨** (GitHub 서버에서 실행)
- ✅ **설정 간단** (5분이면 완료)
- ✅ **로그 자동 저장**
- ✅ **실패 시 이메일 알림**

---

## 🚀 설정 방법 (5분)

### 1단계: GitHub Secrets 설정

1. GitHub 저장소로 이동
   ```
   https://github.com/SJBiber/kdt_woongin
   ```

2. **Settings** → **Secrets and variables** → **Actions** 클릭

3. **New repository secret** 버튼 클릭

4. 다음 4개의 Secret 추가:

   #### Secret 1: YOUTUBE_API_KEY_1
   - Name: `YOUTUBE_API_KEY_1`
   - Value: `첫 번째 YouTube API 키`

   #### Secret 2: YOUTUBE_API_KEY_2
   - Name: `YOUTUBE_API_KEY_2`
   - Value: `두 번째 YouTube API 키`

   #### Secret 3: SUPABASE_URL
   - Name: `SUPABASE_URL`
   - Value: `Supabase URL`

   #### Secret 4: SUPABASE_KEY
   - Name: `SUPABASE_KEY`
   - Value: `Supabase Service Role Key`

---

### 2단계: 워크플로우 파일 Push

이미 완료되었습니다! `.github/workflows/collect.yml` 파일이 생성되었습니다.

---

### 3단계: 자동 실행 확인

1. GitHub 저장소의 **Actions** 탭으로 이동

2. **YouTube 트렌드 자동 수집** 워크플로우 확인

3. **Run workflow** 버튼으로 수동 테스트 가능

---

## ⏰ 실행 시간

- **자동 실행**: 매일 오전 9시 (KST)
- **수동 실행**: Actions 탭에서 언제든지 가능

---

## 📊 로그 확인

1. **Actions** 탭 → 워크플로우 클릭
2. 각 실행 결과 확인
3. **Artifacts**에서 로그 파일 다운로드 가능

---

## 🔧 시간 변경

`.github/workflows/collect.yml` 파일의 cron 설정 수정:

```yaml
schedule:
  # 매일 오전 9시 (KST)
  - cron: '0 0 * * *'  # UTC 00:00 = KST 09:00
  
  # 다른 시간 예시:
  # - cron: '0 12 * * *'  # KST 21:00 (오후 9시)
  # - cron: '0 */6 * * *'  # 6시간마다
```

---

## ⚠️ 주의사항

### API 키 보안
- ❌ `.env` 파일을 Git에 올리지 마세요
- ✅ GitHub Secrets에만 저장하세요
- ✅ `.gitignore`에 `config/.env` 포함됨

### 할당량
- GitHub Actions: 월 2,000분 (충분함)
- YouTube API: 일일 10,000 유닛 (2개 키 사용)

---

## 🧪 테스트

### 수동 실행으로 테스트

1. GitHub → **Actions** 탭
2. **YouTube 트렌드 자동 수집** 클릭
3. **Run workflow** → **Run workflow** 버튼 클릭
4. 실행 결과 확인

---

## ✅ 완료 체크리스트

- [ ] GitHub Secrets 4개 추가
- [ ] 워크플로우 파일 push
- [ ] Actions 탭에서 수동 테스트
- [ ] 내일 오전 9시에 자동 실행 확인

---

## 💡 장점 요약

| 항목 | Cron (Mac) | GitHub Actions |
|------|------------|----------------|
| PC 켜둬야 함 | ✅ 필요 | ❌ 불필요 |
| 비용 | 전기세 | 무료 |
| 설정 난이도 | 쉬움 | 매우 쉬움 |
| 로그 관리 | 수동 | 자동 |
| 실패 알림 | 없음 | 이메일 |

---

**이제 PC를 꺼도 매일 자동으로 데이터가 수집됩니다!** 🎉
