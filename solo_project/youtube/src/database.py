from supabase import create_client, Client
from configs.settings import settings

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def save_top_videos(self, data: list):
        """수집된 인기 동영상 데이터를 테이블에 저장합니다."""
        if not data: return
        self.supabase.table("youtube_top_10").insert(data).execute()
