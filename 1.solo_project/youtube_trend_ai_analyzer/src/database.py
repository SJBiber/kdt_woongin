from supabase import create_client, Client
import pandas as pd
from configs.settings import settings

class TrendDatabase:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def fetch_latest_video_keywords(self, analysis_type="TRENDING", limit=20):
        """가장 최근에 수집된 영상들의 키워드 및 조회수 데이터를 가져옵니다."""
        response = self.supabase.table("youtube_top_10") \
            .select("title, keywords, analysis_type, view_count") \
            .eq("analysis_type", analysis_type) \
            .order("collected_at", desc=True) \
            .limit(limit) \
            .execute()
        
        return pd.DataFrame(response.data)

    def save_category_trends(self, data: list):
        """AI가 분석한 카테고리별 집계 데이터를 DB에 저장합니다."""
        if not data: return
        self.supabase.table("youtube_category_trends").insert(data).execute()
