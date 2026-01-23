"""
네이버 뉴스 댓글 수집 메인 스크립트
키워드 입력 → 뉴스 검색 → 댓글 크롤링 → DB 저장
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.collector.news_searcher import NaverNewsSearcher
from src.collector.comment_crawler import NaverCommentCrawler
from database.supabase_manager import SupabaseManager
from config.settings import validate_config, MAX_NEWS_COUNT, MAX_COMMENTS_PER_NEWS
import time


def collect_and_save_comments(keyword: str, max_news: int = MAX_NEWS_COUNT, 
                               max_comments: int = MAX_COMMENTS_PER_NEWS):
    """
    키워드로 뉴스 검색 후 댓글 수집 및 DB 저장
    
    Args:
        keyword: 검색 키워드
        max_news: 최대 뉴스 수
        max_comments: 뉴스당 최대 댓글 수
    """
    print("=" * 60)
    print("🚀 네이버 뉴스 댓글 수집 시작")
    print("=" * 60)
    print(f"📌 검색 키워드: {keyword}")
    print(f"📌 수집 뉴스 수: 최대 {max_news}개")
    print(f"📌 뉴스당 댓글 수: 최대 {max_comments}개")
    print("=" * 60)
    
    # 1. 환경 설정 검증
    try:
        validate_config()
    except ValueError as e:
        print(f"\n❌ {e}")
        return
    
    # 2. 뉴스 검색
    searcher = NaverNewsSearcher()
    news_list = searcher.search_news(keyword, max_news)
    
    if not news_list:
        print("\n❌ 검색된 뉴스가 없습니다.")
        return
    
    print(f"\n✅ 총 {len(news_list)}개 뉴스 발견")
    
    # 3. 댓글 크롤링 및 DB 저장
    crawler = NaverCommentCrawler(headless=True)
    db = SupabaseManager()
    
    total_comments = 0
    total_saved = 0
    
    for idx, news in enumerate(news_list, 1):
        print(f"\n{'=' * 60}")
        print(f"[{idx}/{len(news_list)}] {news['title'][:50]}...")
        print(f"URL: {news['link']}")
        print(f"{'=' * 60}")
        
        # 댓글 크롤링
        comments = crawler.crawl_comments(news['link'], max_comments)
        total_comments += len(comments)
        
        if not comments:
            print("⚠️  댓글이 없거나 수집 실패")
            continue
        
        # 중복 체크 및 필터링
        new_comments = []
        for comment in comments:
            if not db.comment_exists(comment['comment_id']):
                new_comments.append(comment)
        
        if not new_comments:
            print(f"⚠️  모든 댓글이 이미 DB에 존재함 (중복 {len(comments)}개)")
            continue
        
        print(f"💾 새로운 댓글 {len(new_comments)}개 저장 중...")
        
        # DB 저장
        saved_count = db.insert_comments_batch(new_comments)
        total_saved += saved_count
        
        # 요청 간격 조절 (과도한 크롤링 방지)
        if idx < len(news_list):
            print("⏳ 다음 뉴스 처리까지 3초 대기...")
            time.sleep(3)
    
    # 4. 크롤러 종료
    crawler.close()
    
    # 5. 결과 요약
    print("\n" + "=" * 60)
    print("✅ 수집 완료!")
    print("=" * 60)
    print(f"📊 처리한 뉴스: {len(news_list)}개")
    print(f"📊 수집한 댓글: {total_comments}개")
    print(f"📊 저장한 댓글: {total_saved}개")
    print(f"📊 중복 제외: {total_comments - total_saved}개")
    print("=" * 60)


def main():
    """메인 함수"""
    print("\n🔍 네이버 뉴스 댓글 수집기")
    print("-" * 60)
    
    # 키워드 입력
    keyword = input("검색 키워드를 입력하세요: ").strip()
    
    if not keyword:
        print("❌ 키워드를 입력해주세요.")
        return
    
    # 수집 시작
    collect_and_save_comments(keyword)


if __name__ == "__main__":
    main()
