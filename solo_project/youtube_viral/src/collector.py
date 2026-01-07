from googleapiclient.discovery import build
from configs.settings import settings
from datetime import datetime, timezone, timedelta

class YouTubeCollector:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME,
            settings.YOUTUBE_API_VERSION,
            developerKey=self.api_key
        )

    def get_trending_videos(self, region_code='KR', max_results=300):
        """인기 급상승 영상 목록을 페이지네이션을 사용하여 수집합니다."""
        results = []
        next_page_token = None
        
        while len(results) < max_results:
            results_to_fetch = min(50, max_results - len(results))
            request = self.youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=results_to_fetch,
                pageToken=next_page_token
            )
            response = request.execute()
            items = response.get("items", [])
            if not items:
                break
                
            results.extend(items)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
                
        return results[:max_results]

    def search_by_keyword(self, keyword: str, max_results=50):
        """키워드 검색 결과를 가져옵니다. (최근 7일 데이터로 한정)"""
        # 최근 7일 전 시간 계산 (RFC 3339 형식: YYYY-MM-DDTHH:MM:SSZ)
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace("+00:00", "Z")
        
        request = self.youtube.search().list(
            q=keyword,
            part="snippet",
            type="video",
            regionCode="KR",
            relevanceLanguage="ko",
            maxResults=max_results,
            order="relevance",
            publishedAfter=seven_days_ago
        )
        response = request.execute()
        return response.get("items", [])

    def get_video_stats(self, video_ids: list):
        """영상 ID 리스트에 대한 상세 통계를 수집합니다."""
        if not video_ids: return []
        results = []
        # YouTube API는 단일 요청당 최대 50개의 ID만 허용합니다.
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=",".join(chunk)
            )
            response = request.execute()
            for item in response.get("items", []):
                results.append({
                    "video_id": item["id"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "published_at": item["snippet"]["publishedAt"],
                    "title": item["snippet"]["title"],
                    "collected_at": datetime.now(timezone.utc).isoformat()
                })
        return results
