import logging
import argparse
import os
from collector.youtube_collector import YouTubeCollector
from collector.community_collector import YouTubeCommunityCollector
from database.supabase_client import SupabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_url(url, limit, db_manager):
    if "/post/" in url or "community" in url:
        logger.info(f"커뮤니티 포스트 URL 감지: {url}")
        collector = YouTubeCommunityCollector(headless=True)
        is_community = True
    else:
        logger.info(f"일반 영상 URL 감지: {url}")
        collector = YouTubeCollector()
        is_community = False
        
    try:
        logger.info(f"수집 시작: {url}")
        # 수집 시도 (내부에서 에러가 나거나 중단되어도 예외처리로 저장 시도)
        comments = collector.fetch_comments(url, limit=limit)
        
        if comments:
            logger.info(f"데이터베이스 저장 중 ({len(comments)}건)...")
            db_manager.upsert_comments(comments)
            return True
    except Exception as e:
        logger.error(f"수집 중 오류 발생: {e}")
    finally:
        if is_community:
            collector.close()
    return False

def main():
    parser = argparse.ArgumentParser(description="유튜브 댓글 수집 및 Supabase 저장 프로그램")
    parser.add_argument("--url", type=str, help="수집할 유튜브 영상 URL (단일)")
    parser.add_argument("--file", type=str, default="youtube_link.txt", help="URL 목록이 적힌 파일 경로 (기본: youtube_link.txt)")
    parser.add_argument("--limit", type=int, default=100, help="영상당 수집할 댓글 최대 개수")
    
    args = parser.parse_args()
    db_manager = SupabaseManager()
    
    urls = []
    if args.url:
        urls.append(args.url)
    elif os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        logger.info(f"파일({args.file})에서 {len(urls)}개의 URL을 로드했습니다.")
    
    if not urls:
        logger.error("처리할 URL이 없습니다.")
        return

    for i, url in enumerate(urls):
        logger.info(f"[{i+1}/{len(urls)}] 처리 중: {url}")
        process_url(url, args.limit, db_manager)
        # 한 영상 처리가 끝나면 중간에 분석을 돌려볼 수도 있지만, 일단 수집에 집중

if __name__ == "__main__":
    main()
