import os
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def delete_keyword_data(table_name, keyword):
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("[!] .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
        return

    supabase: Client = create_client(url, key)
    
    try:
        print(f"[*] {table_name} 테이블에서 keyword='{keyword}'인 데이터를 삭제하는 중...")
        response = supabase.table(table_name).delete().eq("keyword", keyword).execute()
        print(f"[+] 삭제 완료: {len(response.data)}개의 행이 삭제되었습니다.")
    except Exception as e:
        print(f"[!] 삭제 중 오류 발생: {e}")

if __name__ == "__main__":
    delete_keyword_data("naver_blog_trends", "포켓몬빵")
