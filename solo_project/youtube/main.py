from src.collector import YouTubeCollector
from src.processor import KeywordProcessor
from src.database import DatabaseManager
from configs.settings import settings
from datetime import datetime

def run_analysis(analysis_type="TRENDING"):
    print(f"--- [{datetime.now()}] YouTube {analysis_type} Top {settings.ANALYSIS_LIMIT} Analysis Started ---")
    
    collector = YouTubeCollector()
    processor = KeywordProcessor()
    db = DatabaseManager()

    try:
        # 1. 데이터 수집
        if analysis_type == "TRENDING":
            videos = collector.get_trending_videos(limit=settings.ANALYSIS_LIMIT)
        else: # HISTORICAL
            videos = collector.get_historical_top_videos(limit=settings.ANALYSIS_LIMIT)
            
        print(f"Successfully fetched {len(videos)} videos.")

        formatted_data = []
        for i, v in enumerate(videos):
            keywords = processor.process_video_keywords(v)
            
            item = {
                "rank": i + 1,
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "channel_title": v["snippet"]["channelTitle"],
                "view_count": int(v["statistics"].get("viewCount", 0)),
                "like_count": int(v["statistics"].get("likeCount", 0)),
                "comment_count": int(v["statistics"].get("commentCount", 0)),
                "keywords": keywords,
                "analysis_type": analysis_type,
                "uploaded_at": v["snippet"]["publishedAt"]
            }
            formatted_data.append(item)
            print(f"Rank {item['rank']}: {item['title'][:40]}... ({item['view_count']:,} views)")

        # 2. DB 저장
        db.save_top_videos(formatted_data)
        print(f"Saved {len(formatted_data)} records ({analysis_type}) to Supabase.")

    except Exception as e:
        print(f"Error occurred in {analysis_type}: {e}")

if __name__ == "__main__":
    # 1. 실시간 인기 급상승 Top 20 분석
    run_analysis(analysis_type="TRENDING")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 지난 일주일간 조회수 Top 20 분석
    run_analysis(analysis_type="HISTORICAL")
