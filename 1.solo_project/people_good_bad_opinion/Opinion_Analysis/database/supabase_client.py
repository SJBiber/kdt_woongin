import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# .env 로드 (절대 경로 혹은 현재 작업 디렉토리 기준)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.error("Supabase URL or Key is missing in .env file.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized.")

    def upsert_comments(self, data_list):
        """임성근 유튜브 댓글 리스트를 Supabase 테이블에 Upsert합니다."""
        if not self.client:
            logger.error("Supabase client not initialized.")
            return False

        if not data_list:
            logger.warning("No data to upsert.")
            return True

        try:
            # comment_id를 기준으로 중복 방지 (ON CONFLICT)
            response = self.client.table("im_sung_gen_youtube_comments").upsert(
                data_list, 
                on_conflict="comment_id"
            ).execute()
            logger.info(f"Successfully upserted {len(data_list)} comments.")
            return True
        except Exception as e:
            logger.error(f"Error upserting data to Supabase: {e}")
            return False

    def upsert_baek_jongwon_comments(self, data_list):
        """백종원 유튜브 댓글 리스트를 Supabase 테이블에 Upsert합니다."""
        if not self.client:
            logger.error("Supabase client not initialized.")
            return False

        if not data_list:
            logger.warning("No data to upsert.")
            return True

        try:
            # comment_id를 기준으로 중복 방지 (ON CONFLICT)
            response = self.client.table("baek_jongwon_youtube_comments").upsert(
                data_list, 
                on_conflict="comment_id"
            ).execute()
            logger.info(f"Successfully upserted {len(data_list)} Baek Jongwon comments.")
            return True
        except Exception as e:
            logger.error(f"Error upserting Baek Jongwon data to Supabase: {e}")
            return False

    def upsert_video_stats(self, data_list):
        """영상 통계 리스트를 Supabase 테이블에 Upsert합니다."""
        if not self.client:
            logger.error("Supabase client not initialized.")
            return False

        if not data_list:
            logger.warning("No data to upsert.")
            return True

        try:
            # video_id를 기준으로 중복 방지 (ON CONFLICT)
            response = self.client.table("video_stats").upsert(
                data_list, 
                on_conflict="video_id"
            ).execute()
            logger.info(f"Successfully upserted {len(data_list)} video stats.")
            return True
        except Exception as e:
            logger.error(f"Error upserting video stats to Supabase: {e}")
            return False

if __name__ == "__main__":
    db = SupabaseManager()
    # 테스트 데이터
    test_data = [{
        "comment_id": "test_id_1",
        "video_id": "test_video",
        "author": "tester",
        "content": "테스트 댓글입니다.",
        "likes": 10,
        "published_at": "2024-03-21T00:00:00Z"
    }]
    db.upsert_comments(test_data)
