import os
import re
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
from supabase import create_client, Client

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

class YouTubeScraper:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env file")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        
        # Supabase 초기화
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def search_videos(self, query, published_after=None, published_before=None, max_results=10):
        """특정 기간의 비디오 검색"""
        request = self.youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            publishedAfter=published_after,
            publishedBefore=published_before,
            maxResults=max_results,
            order="relevance" # 또는 viewCount
        )
        response = request.execute()
        
        videos = []
        for item in response.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "channel_title": item["snippet"]["channelTitle"]
            })
        return videos

    def get_video_comments(self, video_id, max_results=100):
        """비디오의 댓글 수집"""
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText"
            )
            response = request.execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "comment_id": item["id"],
                    "video_id": video_id,
                    "author": snippet["authorDisplayName"],
                    "text": snippet["textDisplay"],
                    "published_at": snippet["publishedAt"],
                    "like_count": snippet["likeCount"]
                })
        except Exception as e:
            print(f"⚠️ Error fetching comments for {video_id}: {e}")
            
        return comments

    def save_comments_to_supabase(self, comments):
        """수집된 댓글을 Supabase에 저장 (또는 분석용 데이터셋 구성)"""
        if not comments:
            return
        
        # 테이블 이름은 프로젝트 상황에 맞게 조정 (예: youtube_comments)
        # 여기서는 일단 분석 결과를 위해 리턴하거나 특정 테이블에 upsert
        try:
            # 중복 방지를 위한 upsert (comment_id 기준)
            data = self.supabase.table("youtube_comments").upsert(comments).execute()
            print(f"✅ Saved {len(comments)} comments to Supabase.")
        except Exception as e:
            print(f"❌ Supabase Save Error: {e}")

if __name__ == "__main__":
    scraper = YouTubeScraper()
    
    # 분석 시기 설정
    periods = [
        {"name": "성숙기(현재)", "after": "2026-01-01T00:00:00Z", "before": "2026-01-14T23:59:59Z"},
        {"name": "도입기(과거)", "after": "2025-10-01T00:00:00Z", "before": "2025-11-30T23:59:59Z"}
    ]
    
    keyword = "두바이 쫀득 쿠키"
    
    for period in periods:
        print(f"\n📺 Analyzing Period: {period['name']}")
        videos = scraper.search_videos(keyword, published_after=period["after"], published_before=period["before"], max_results=5)
        
        for v in videos:
            print(f"  🔍 Video: {v['title']} ({v['published_at']})")
            comments = scraper.get_video_comments(v["video_id"], max_results=50)
            # scraper.save_comments_to_supabase(comments) # 테이블 생성 후 주석 해제
            print(f"     -> Collected {len(comments)} comments")
