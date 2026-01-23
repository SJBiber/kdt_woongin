# 🚀 빠른 시작 가이드

## 1️⃣ 데이터베이스 설정 (최초 1회)

### Supabase에서 테이블 생성
1. [Supabase](https://supabase.com) 접속
2. 프로젝트 선택
3. **SQL Editor** 클릭
4. `schema.sql` 파일 내용 복사 & 붙여넣기
5. **Run** 클릭

✅ `daily_video_trends` 테이블이 생성됩니다!

---

## 2️⃣ 환경 설정 확인

### `.env` 파일 확인
```bash
cat .env
```

다음 항목이 있는지 확인:
```
YOUTUBE_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

---

## 3️⃣ 실행

### 트렌드 추적 시작
```bash
python3 tracker.py
```

### 예상 출력
```
[✓] 데이터베이스 연결 성공
[✓] YouTube API 연결 성공

============================================================
[*] 트렌드 추적 시작
    키워드: 임성근 쉐프
    수집 날짜: 2026-01-22
    추적 기간: 365일
============================================================

[1/365] 처리 중: 2026-01-21 업로드 영상...
  → 영상: 5개 | 조회수: 12,345 (첫 수집)
[+] 저장 완료: 임성근 쉐프 | 업로드: 2026-01-21 | 수집: 2026-01-22 | 조회수: 12,345

[2/365] 처리 중: 2026-01-20 업로드 영상...
  → 영상: 8개 | 조회수: 45,678 (+2,345, +5.4%)
[+] 저장 완료: 임성근 쉐프 | 업로드: 2026-01-20 | 수집: 2026-01-22 | 조회수: 45,678

...
```

---

## 4️⃣ 데이터 확인

### Supabase에서 확인
1. Supabase 프로젝트 → **Table Editor**
2. `daily_video_trends` 테이블 선택
3. 데이터 확인!

### SQL로 확인
```sql
-- 최신 데이터 조회
SELECT * FROM daily_video_trends
WHERE keyword = '임성근 쉐프'
ORDER BY collected_date DESC, upload_date DESC
LIMIT 10;
```

---

## 5️⃣ 매일 자동 실행 (선택사항)

### Mac/Linux - Cron
```bash
# crontab 편집
crontab -e

# 매일 오전 9시 실행 추가
0 9 * * * cd /Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker && python3 tracker.py >> log.txt 2>&1
```

### Windows - 작업 스케줄러
1. `작업 스케줄러` 실행
2. `기본 작업 만들기` 클릭
3. 이름: "YouTube 트렌드 추적"
4. 트리거: 매일 오전 9시
5. 동작: `python tracker.py` 실행

---

## 6️⃣ 설정 변경

### 키워드 변경
`tracker.py` 파일 열기:
```python
# 143번째 줄 근처
keyword = "임성근 쉐프"  # ← 여기를 원하는 키워드로 변경
```

### 추적 기간 변경
```python
# 144번째 줄 근처
lookback_days = 365  # ← 30, 90, 180 등으로 변경 가능
```

---

## ⚠️ 주의사항

### API 할당량
- YouTube API는 **하루 10,000 유닛** 제한
- 365일 추적 시 약 **3,650 유닛** 소모
- 할당량 초과 시 다음날 자동 재개

### 권장 사항
1. **처음엔 30일만**: `lookback_days = 30`으로 시작
2. **점진적 확장**: 문제없으면 90일, 180일, 365일로 확대
3. **매일 실행**: 한 번에 365일 수집보다, 매일 조금씩 수집

---

## 🆘 문제 해결

### "API 할당량 초과" 메시지
→ 정상입니다! 내일 다시 실행하세요.

### "데이터베이스 연결 실패"
→ `.env` 파일의 Supabase 정보 확인

### "모듈을 찾을 수 없음"
→ `pip install -r requirements.txt` 실행

---

## 📊 다음 단계

1. ✅ 데이터 수집 완료
2. 📈 대시보드 만들기 (Streamlit)
3. 📧 알림 설정 (급격한 변화 감지)
4. 🔄 자동화 (매일 실행)

---

**문의사항이 있으면 README.md를 참고하세요!** 🚀
