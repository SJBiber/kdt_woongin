import os
import sys
import io
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class SupabaseManager:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("[!] .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 올바르게 설정해주세요.")
            
        self.supabase: Client = create_client(url, key)

    def insert_blog_trend(self, data):
        """
        네이버 블로그 트렌드 데이터를 naver_blog_trends 테이블에 삽입/업데이트합니다.
        data: { "date": "YYYY-MM-DD", "keyword": "...", "total_count": 0 }
        """
        try:
            # upsert based on (date, keyword) unique constraint
            response = self.supabase.table("naver_blog_trends").upsert(
                data,
                on_conflict="date,keyword"
            ).execute()
            return response
        except Exception as e:
            print(f"[!] DB 저장 중 오류 발생 ({data.get('date', 'unknown')}): {e}")
            return None
