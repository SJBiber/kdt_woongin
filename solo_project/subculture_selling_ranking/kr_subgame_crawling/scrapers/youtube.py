import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class YouTubeScraper:
    def __init__(self):
        self.api_key = os.environ.get("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("환경 변수에서 YOUTUBE_API_KEY를 찾을 수 없습니다.")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_video_stats(self, keyword: str, days=1):
        """
        주어진 키워드에 대해 최근 업로드 수와 주요 영상 지표를 가져옵니다.
        """
        # RFC3339 형식의 타임스탬프 계산 (publishedAfter 용)
        after_date = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"

        # 1. 최근 24시간 업로드 영상 수 조회
        search_response = self.youtube.search().list(
            q=keyword,
            part="id,snippet",
            maxResults=50,
            publishedAfter=after_date,
            type="video"
        ).execute()

        upload_count = search_response.get("pageInfo", {}).get("totalResults", 0)

        # 2. 상위 영상 정보 조회 (조회수 기준)
        top_videos_response = self.youtube.search().list(
            q=keyword,
            part="id,snippet",
            maxResults=5,
            order="viewCount",
            type="video"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in top_videos_response.get("items", [])]
        
        video_details = []
        if video_ids:
            stats_response = self.youtube.videos().list(
                id=",".join(video_ids),
                part="statistics,snippet"
            ).execute()

            for item in stats_response.get("items", []):
                video_details.append({
                    "title": item["snippet"]["title"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                    "published_at": item["snippet"]["publishedAt"]
                })

        return {
            "keyword": keyword,
            "upload_count_24h": upload_count,
            "top_videos": video_details
        }

if __name__ == "__main__":
    # 테스트 실행
    try:
        scraper = YouTubeScraper()
        result = scraper.get_video_stats("블루 아카이브")
        print(result)
    except Exception as e:
        print(f"테스트 실패: {e}")
