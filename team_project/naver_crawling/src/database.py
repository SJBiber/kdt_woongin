import os
from supabase import create_client, Client
from dotenv import load_dotenv

from pathlib import Path

# 설정 로드 - config/.env
config_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

class SupabaseClient:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        self.supabase: Client = create_client(url, key)

    def upsert_blog_counts(self, data: list):
        """
        data: list of dicts with keys ['keyword', 'target_date', 'post_count']
        """
        if not data:
            return
        
        # upsert based on (keyword, target_date) unique constraint
        # ensure you have an index or unique constraint on (keyword, target_date) in your supabase table
        response = self.supabase.table("naver_blog_counts").upsert(
            data,
            on_conflict="keyword,target_date"
        ).execute()
        return response
