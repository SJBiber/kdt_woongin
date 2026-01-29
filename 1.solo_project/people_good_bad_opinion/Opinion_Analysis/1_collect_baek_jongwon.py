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

def process_url(url, limit, db_manager, collection_period):
    """
    백종원 관련 영상 댓글 수집
    
    Args:
        url: 유튜브 영상 URL
        limit: 수집할 댓글 최대 개수
        db_manager: Supabase 매니저
        collection_period: 'controversy' (논란시기) 또는 'current' (현재)
    """
    if "/post/" in url or "community" in url:
        logger.info(f"커뮤니티 포스트 URL 감지: {url}")
        collector = YouTubeCommunityCollector(headless=True)
        is_community = True
    else:
        logger.info(f"일반 영상 URL 감지: {url}")
        collector = YouTubeCollector()
        is_community = False
        
    try:
        logger.info(f"수집 시작: {url} (시기: {collection_period})")
        comments = collector.fetch_comments(url, limit=limit)
        
        if comments:
            # collection_period 필드 추가
            for comment in comments:
                comment['collection_period'] = collection_period
                comment['target_person'] = '백종원'  # 분석 대상 구분
            
            logger.info(f"데이터베이스 저장 중 ({len(comments)}건)...")
            # 백종원 전용 테이블에 저장
            db_manager.upsert_baek_jongwon_comments(comments)
            return True
    except Exception as e:
        logger.error(f"수집 중 오류 발생: {e}")
    finally:
        if is_community:
            collector.close()
    return False

def main():
    parser = argparse.ArgumentParser(description="백종원 유튜브 댓글 수집 프로그램")
    parser.add_argument("--url", type=str, help="수집할 유튜브 영상 URL (단일)")
    parser.add_argument("--file", type=str, default="baek_jongwon_link.txt", 
                       help="URL 목록 파일 (기본: baek_jongwon_link.txt)")
    parser.add_argument("--limit", type=int, default=500, 
                       help="영상당 수집할 댓글 최대 개수 (기본: 500)")
    parser.add_argument("--period", type=str, choices=['controversy', 'current'], 
                       default='controversy',
                       help="수집 시기 구분 (controversy: 논란시기 2025.02-03, current: 현재 2025.12-2026.01)")
    
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
        logger.info(f"'{args.file}' 파일에 YouTube URL을 추가하세요.")
        return

    logger.info(f"\n{'='*60}")
    logger.info(f"백종원 댓글 수집 시작")
    logger.info(f"수집 시기: {args.period}")
    logger.info(f"총 {len(urls)}개 영상")
    logger.info(f"영상당 최대 {args.limit}개 댓글")
    logger.info(f"{'='*60}\n")

    success_count = 0
    for i, url in enumerate(urls):
        logger.info(f"[{i+1}/{len(urls)}] 처리 중: {url}")
        if process_url(url, args.limit, db_manager, args.period):
            success_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"수집 완료: {success_count}/{len(urls)} 성공")
    logger.info(f"{'='*60}\n")

if __name__ == "__main__":
    main()
