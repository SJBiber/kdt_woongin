import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from scraper import NaverScraper
from database import SupabaseClient

def main():
    # 1. 수집 키워드 설정 (필요에 따라 수정 가능)
    # 기본적으로는 실행 시 인자로 받거나 리스트를 정의합니다.
    keywords = ["두바이 초코 쿠키"] 
    if len(sys.argv) > 1:
        keywords = sys.argv[1:]

    days_back = 180
    
    # 종료일: 어제 (금일 - 1)
    # 시작일: 180일 전
    end_date = (datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59)
    start_date = (datetime.now() - timedelta(days=days_back)).replace(hour=0, minute=0, second=0)
    
    print(f"=== 네이버 블로그 포스팅 수집 시작 ===")
    print(f"수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"대상 키워드: {', '.join(keywords)}")
    print("-" * 40)

    try:
        scraper = NaverScraper()
        db = SupabaseClient()
    except Exception as e:
        print(f"초기화 요류: {e}")
        return

    for keyword in keywords:
        # 2. 날짜별 루프를 통한 180일치 데이터 수집 (API 1000개 제한 우회 전략)
        upload_data = scraper.fetch_all_180_days(keyword, days=days_back)
        
        # 3. DB 저장
        if upload_data:
            print(f"[{keyword}] {len(upload_data)}일치 데이터를 DB에 업로드 시도 중...")
            try:
                db.upsert_blog_counts(upload_data)
                print(f"[{keyword}] 성공적으로 저장되었습니다.")
            except Exception as e:
                print(f"[{keyword}] DB 업로드 중 오류 발생: {e}")
        else:
            print(f"[{keyword}] 해당 기간 내에 수집된 데이터가 없습니다.")
        
        print("-" * 40)

    print("모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
