from googleapiclient.discovery import build
from configs.settings import settings
from datetime import datetime, timedelta, timezone

class YouTubeCollector:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME,
            settings.YOUTUBE_API_VERSION,
            developerKey=self.api_key
        )

    def get_trending_videos(self, region_code='KR', limit=20):
        """인기 급상승 영상 상위 N개를 수집합니다."""
        request = self.youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=limit
        )
        response = request.execute()
        return response.get("items", [])

    def get_historical_top_videos(self, region_code='KR', limit=20):
        """최근 7일 이내 업로드된 영상 중 조회수가 가장 높은 N개를 검색합니다."""
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace("+00:00", "Z")
        
        request = self.youtube.search().list(
            part="id",
            q="한국", 
            publishedAfter=seven_days_ago,
            order="viewCount",
            type="video",
            regionCode=region_code,
            maxResults=limit
        )
        response = request.execute()
        video_ids = [item['id']['videoId'] for item in response.get("items", [])]
        
        return self.get_video_details(video_ids)

    def get_video_details(self, video_ids: list):
        """영상 ID 리스트에 대한 상세 통계를 수집합니다."""
        if not video_ids: return []
        request = self.youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        response = request.execute()
        return response.get("items", [])
