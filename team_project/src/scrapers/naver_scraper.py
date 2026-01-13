import requests
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from supabase import create_client, Client

# .env 파일 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../.env")

if os.path.exists(env_path):
    load_dotenv(env_path)

class NaverBlogScraper:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("NAVER_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Supabase 설정
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"

        if not self.client_id or not self.client_secret:
            raise ValueError("Naver API Credentials are missing in .env file.")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase Credentials are missing in .env file.")

        # Supabase 클라이언트 초기화
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def search_blog(self, query, display=100, start=1, sort='sim'):
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        # sort='sim'으로 변경하여 정확도순(유사도순) 수집
        params = {"query": query, "display": display, "start": start, "sort": sort}
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"API Request Error: {e}")
            return None

    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s가-힣.,!?%]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_blog_content(self, url):
        try:
            if "blog.naver.com" in url and "/PostView.naver" not in url:
                parts = url.split("/")
                if len(parts) >= 5:
                    user_id, log_no = parts[3], parts[4]
                    url = f"https://blog.naver.com/PostView.naver?blogId={user_id}&logNo={log_no}"

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            content_div = soup.find("div", class_="se-main-container") or soup.find("div", id="postViewArea")
            return content_div.get_text(separator=" ").strip() if content_div else ""
        except Exception:
            return ""

    def save_to_supabase(self, data):
        try:
            # raw_content는 저장하지 않도록 변경
            response = self.supabase.table("blog_review").upsert({
                "title": data['title'],
                "link": data['link'],
                "postdate": data['postdate'],
                "address": data['address'],
                "clean_content": data['clean_content']
            }).execute()
            return response
        except Exception as e:
            # 중복 키 에러(23505) 또는 중복 문구 포함 시 무시
            error_str = str(e).lower()
            if '23505' in error_str or 'duplicate key' in error_str:
                return None
            print(f"Supabase Save Error: {e}")
            return None

if __name__ == "__main__":
    scraper = NaverBlogScraper()
    
    # 서울시 25개 자치구 리스트
    seoul_districts = [
        "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
        "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구",
        "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
    ]
    
    # 검색 키워드 다양화 (중복 회피용)
    search_keywords = ["두바이 쫀득 쿠키 맛집", "두바이 초콜릿 쿠키", "두바이 쿠키 파는곳", "두바이 쫀득쿠키 후기"]
    
    total_collected = 0
    target_total = 300 # 1000개에서 300개로 하향 조정
    
    print(f"🚀 Starting Diverse Small Scale Collection (Target: {target_total} Seoul items)...")

    for keyword in search_keywords:
        if total_collected >= target_total: break
        
        for district in seoul_districts:
            if total_collected >= target_total: break
            
            query = f"서울 {district} {keyword}"
            print(f"\n🔎 Searching: [{query}] (Unique Found: {total_collected})")
            
            # 300개 목표에 맞춰 지역별 수집 개수를 20개로 제한하여 골고루 수집
            search_result = scraper.search_blog(query, display=20, start=1)
            
            if not search_result or 'items' not in search_result:
                continue
                
            items = search_result.get("items", [])
            for idx, item in enumerate(items):
                # 제목에서 HTML 태그 제거 (<b> 등)
                clean_title = scraper.clean_text(item['title'])
                
                raw_content = scraper.get_blog_content(item['link'])
                if not raw_content: continue
                
                clean_content = scraper.clean_text(raw_content)
                
                # 2. 주소 및 상호명 추출 시도
                addr_pattern = rf"(서울특별시|서울시)\s+([가-힣]*{district}[가-힣]*)\s+([가-힣\d\s-]+(로|길|동|가|번지))"
                match = re.search(addr_pattern, clean_content)
                
                # 타 지역 키워드 체크 (매우 엄격하게)
                other_regions = ["제주", "부산", "대구", "인천", "광주", "대전", "울산", "수원", "성남", "고양", "용인", "천안", "청주"]
                # 본문 시작 혹은 특정 키워드 주변에 타 지역이 있으면 스킵
                if any(region in clean_content[:150] for region in other_regions) and district not in clean_content[:100]:
                    continue

                if match:
                    address = match.group(0)
                else:
                    # 상세 주소가 없더라도 서울 데이터임이 확실치 않으면 저장하지 않음 (선택)
                    # 여기서는 수집 효율을 위해 상세 주소가 없으면 스킵합니다.
                    continue

                db_data = {
                    'title': clean_title, 
                    'link': item['link'], 
                    'postdate': item['postdate'],
                    'address': address, 
                    'clean_content': clean_content
                }
                
                if scraper.save_to_supabase(db_data):
                    total_collected += 1
                    if total_collected % 10 == 0:
                        print(f"✅ Unique Collected: {total_collected}...")
                
                if total_collected >= target_total:
                    break

    print(f"\n✨ Mission Accomplished! Total {total_collected} Seoul data synced to Supabase.")
