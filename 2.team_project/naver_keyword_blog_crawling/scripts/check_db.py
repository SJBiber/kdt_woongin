import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

res = supabase.table("naver_blog_trends").select("id", count="exact").order("id", desc=True).limit(5).execute()
print(f"Total rows: {res.count}")
print(f"Top IDs: {[item['id'] for item in res.data]}")
