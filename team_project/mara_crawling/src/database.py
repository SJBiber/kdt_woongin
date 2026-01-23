import os
import sys
import io
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 표준 출력을 UTF-8로 재설정 (Windows 한글 깨짐 방지)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SupabaseManager:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or url == "YOUR_SUPABASE_URL" or not key or key == "YOUR_SUPABASE_ANON_KEY":
            raise ValueError("[!] .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 올바르게 설정해주세요.")
            
        self.supabase: Client = create_client(url, key)

    def insert_blog_trend(self, data):
        """
        네이버 블로그 트렌드 데이터를 mara_trends 테이블에 삽입/업데이트합니다.
        data 예시:
        {
            "date": "2026-01-13",
            "keyword": "마라샹궈",
            "total_count": 2719
        }
        """
        try:
            response = self.supabase.table("mara_trends").upsert(
                data,
                on_conflict="date,keyword"
            ).execute()
            return response
        except Exception as e:
            print(f"[!] DB 저장 중 오류 발생 ({data.get('date', 'unknown')}): {e}")
            return None

if __name__ == "__main__":
    # 테스트용 코드
    try:
        db = SupabaseManager()
        print("[+] Supabase 연결 성공")
    except Exception as e:
        print(e)
