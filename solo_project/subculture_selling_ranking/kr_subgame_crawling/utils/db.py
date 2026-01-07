import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_supabase_client() -> Client:
    """
    Supabase 클라이언트를 초기화하고 반환합니다.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def upsert_game_data(table_name: str, data: list):
    """
    지정된 테이블에 데이터를 Upsert(추가 또는 업데이트)합니다.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table(table_name).upsert(data).execute()
        return response
    except Exception as e:
        print(f"{table_name} 데이터 저장 중 오류 발생: {e}")
        return None
