import os
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
import io

# .env 파일 로드
load_dotenv()


# 표준 출력을 UTF-8로 재설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SupabaseManager:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("[!] SUPABASE_URL 또는 SUPABASE_KEY가 .env 파일에 설정되어 있지 않습니다.")
            
        self.supabase: Client = create_client(url, key)

    def insert_daily_trend(self, summary_data):
        """
        일별 트렌드 집계 데이터를 daily_trends 테이블에 삽입합니다.
        summary_data 예시:
        {
            "date": "2026-01-13",
            "keyword": "두쫀쿠",
            "video_count": 25,
            "total_views": 2069475,
            "total_likes": 49257,
            "total_comments": 3826
        }
        """
        try:
            response = self.supabase.table("daily_trends").upsert(
                summary_data,
                on_conflict="date,keyword" # 날짜와 키워드가 같으면 업데이트
            ).execute()
            print(f"[+] DB 저장 완료: {summary_data['date']}")
            return response
        except Exception as e:
            print(f"[!] DB 저장 중 오류 발생: {e}")
            return None

if __name__ == "__main__":
    # 테스트용 코드
    try:
        db = SupabaseManager()
        test_data = {
            "date": "2026-01-01",
            "keyword": "테스트",
            "video_count": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0
        }
        db.insert_daily_trend(test_data) # 실제 실행 시 주석 해제
    except Exception as e:
        print(e)
