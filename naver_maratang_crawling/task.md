# Task: 마라탕 네이버 블로그 포스팅 데이터 수집 (AJAX 방식)

2018년 8월 1일부터 2023년 8월 1일까지 '마라탕' 키워드에 대한 네이버 블로그 일별 포스팅 수를 수집하여 Supabase DB에 저장합니다.

## 세부 요구사항
- **대상 키워드**: `마라탕`
- **대상 기간**: `2018-08-01 ~ 2023-08-01`
- **수집 방식**: 네이버 블로그 AJAX API (`https://section.blog.naver.com/ajax/SearchList.naver`) 사용 (API Key 불필요)
- **저장 위치**: 로컬 CSV 파일 (`maratang_blog_counts.csv`)
- **참고 소스**: `kdt_woongin/jw_naver_crawling` 의 로직 및 구조 참조

## 작업 순서
1. `jw_naver_crawling`의 로직을 기반으로 `scraper.py`, `main.py` 작성 (DB 연동 제외)
2. 2018.08.01 ~ 2023.08.01 기간 설정 및 루프 구현
3. 데이터 수집 및 CSV 파일 저장 확인
