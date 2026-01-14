import os  # 운영체제와 통신하기 위한 도구 (환경변수 읽기 등)
from supabase import create_client, Client  # Supabase 데이터베이스를 사용하기 위한 도구
from dotenv import load_dotenv  # .env 파일에 저장된 설정을 읽어오는 도구
import sys  # 파이썬 시스템 설정 도구
import io  # 데이터 입력/출력 처리 도구

# 1. 환경 설정 로드
load_dotenv()  # .env 파일에 작성된 SUPABASE_URL과 KEY를 프로그램에 불러옵니다.

# 한글 출력 깨짐 방지: 터미널 창에서 한글이 잘 보이도록 설정합니다.
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SupabaseManager:
    """데이터베이스(Supabase)와 소통하는 담당자 클래스"""
    
    def __init__(self):
        # .env 파일에서 데이터베이스 주소와 비밀 키를 가져옵니다.
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        # 주소나 키가 없으면 프로그램을 시작할 수 없으므로 경고를 띄웁니다.
        if not url or not key:
            raise ValueError("[!] .env 파일에 Supabase 정보가 설정되어 있는지 확인해주세요.")
            
        # 데이터를 주고받을 '통로(self.supabase)'를 만듭니다.
        self.supabase: Client = create_client(url, key)

    def insert_daily_trend(self, summary_data):
        """
        수집된 일별 데이터를 데이터베이스의 'daily_trends' 테이블에 저장합니다.
        
        summary_data(데이터 꾸러미) 구성 예시:
        {
            "date": "2026-01-13",      # 날짜
            "keyword": "두쫀쿠",         # 검색어
            "video_count": 25,         # 영상 개수
            "total_views": 2069475,    # 총 조회수
            "total_likes": 49257,      # 총 좋아요
            "total_comments": 3826     # 총 댓글
        }
        """
        try:
            # .upsert()를 사용하면:
            # - 같은 날짜/키워드 데이터가 없으면 새로 저장하고,
            # - 이미 데이터가 있으면 새 정보로 덮어씁니다(업데이트).
            response = self.supabase.table("daily_trends").upsert(
                summary_data,
                on_conflict="date,keyword" # 날짜와 키워드를 기준으로 중복을 체크합니다.
            ).execute()
            
            print(f"[+] DB 저장 완료: {summary_data['date']} ({summary_data['keyword']})")
            return response
        except Exception as e:
            # 저장 중에 문제가 생기면 어떤 에러인지 알려줍니다.
            print(f"[!] DB 저장 중 오류가 발생했습니다: {e}")
            return None

# 이 파일을 직접 실행해서 테스트해보고 싶을 때 사용하는 부분입니다.
if __name__ == "__main__":
    try:
        db = SupabaseManager()
        # 테스트용 가짜 데이터
        test_data = {
            "date": "2026-01-01",
            "keyword": "테스트용",
            "video_count": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0
        }
        # 실제로 DB에 넣어보고 싶다면 아래 줄을 사용합니다.
        # db.insert_daily_trend(test_data)
        print("[알림] 데이터베이스 관리 도구가 정상적으로 준비되었습니다.")
    except Exception as e:
        print(f"[오류] 도구 준비 중 문제 발생: {e}")
