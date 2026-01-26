"""
네이버 뉴스 기사만 수집하여 DB에 저장하는 스크립트
(API 전 전용)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.collector.news_searcher import NaverNewsSearcher
from src.collector.comment_crawler import NaverCommentCrawler
from database.supabase_manager import SupabaseManager
from config.settings import validate_config, MAX_NEWS_COUNT
from datetime import datetime
import time


def collect_news_articles(keyword: str, max_news: int = MAX_NEWS_COUNT, end_date: str = None):
    """
    키워드로 뉴스 검색 후 기사 정보만 DB 저장 (날짜 필터 지원)
    """
    print("=" * 60)
    print("🚀 네이버 뉴스 기사 수집 시작")
    print("=" * 60)
    print(f"📌 검색 키워드: {keyword}")
    print(f"📌 수집 기준: {end_date + ' 이전 기사' if end_date else '최신 기사'}")
    print(f"📌 수집 뉴스 수: 최대 {max_news}개")
    print("=" * 60)
    
    # 1. 환경 설정 검증
    try:
        validate_config()
    except ValueError as e:
        print(f"\n❌ {e}")
        return
    
    # 2. 뉴스 검색
    searcher = NaverNewsSearcher()
    # 특정 시점 이전 수집을 위해 end_date 전달
    news_list = searcher.search_news(keyword, max_news, end_date=end_date)
    
    if not news_list:
        print("\n❌ 검색된 뉴스가 없습니다.")
        return
    
    print(f"\n✅ 총 {len(news_list)}개 뉴스 발견")
    
    # 3. DB 저장
    db = SupabaseManager()
    crawler_temp = NaverCommentCrawler()
    
    unique_articles = {} # news_id를 키로 사용하여 중복 제거
    
    for news in news_list:
        news_info = crawler_temp.extract_news_info(news['link'])
        news_id = news_info['news_id']
        
        # 날짜 처리
        pub_date = news.get('pubDate')
        if not pub_date:
            pub_date = datetime.now().isoformat()
            
        article_data = {
            'news_id': news_id,
            'title': news['title'],
            'link': news['link'],
            'description': news.get('description', ''),
            'pub_date': pub_date,
            'origin_link': news.get('originallink', news['link'])
        }
        
        if news_id not in unique_articles:
            unique_articles[news_id] = article_data
    
    articles_to_save = list(unique_articles.values())
    
    if articles_to_save:
        print(f"💾 기사 {len(articles_to_save)}개 저장 중 (중복 제외)...")
        saved_count = db.insert_articles_batch(articles_to_save)
        print(f"✅ {saved_count}개 기사 저장 완료")
    
    print("\n" + "=" * 60)
    print("✅ 기사 수집 완료!")
    print("=" * 60)


if __name__ == "__main__":
    from datetime import datetime
    print("\n🔍 네이버 뉴스 기사 수집기 (News Only)")
    print("-" * 60)
    keyword = input("검색 키워드를 입력하세요: ").strip()
    
    print("\n📅 특정 날짜 이전의 기사를 가져오시겠습니까?")
    print("   형식: YYYY.MM.DD (예: 2026.01.19)")
    print("   엔터를 치면 최신 기사를 가져옵니다.")
    target_date = input("입력: ").strip()
    
    if keyword:
        collect_news_articles(keyword, end_date=target_date if target_date else None)
    else:
        print("❌ 키워드를 입력해주세요.")
