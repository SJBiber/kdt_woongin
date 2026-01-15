import requests
import json
import pandas as pd
import time
from datetime import datetime, timedelta
from urllib.parse import quote
import os
from database import SupabaseManager

class NaverBlogCrawler:
    def __init__(self):
        self.url = "https://section.blog.naver.com/ajax/SearchList.naver"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        # DB 연동 비활성화 (CSV에만 저장)
        self.db = None
        print("[*] DB 저장이 비활성화되었습니다. CSV 파일에만 기록됩니다.")

    def get_blog_count(self, keyword, start_date="", end_date=""):
        params = {
            "countPerPage": "7",
            "currentPage": "1",
            "startDate": start_date,
            "endDate": end_date,
            "keyword": keyword,
            "orderBy": "sim"
        }
        
        # Add referer dynamically
        headers = self.headers.copy()
        headers["Referer"] = f"https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword={quote(keyword)}"
        
        try:
            response = requests.get(self.url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"[-] HTTP Error {response.status_code} for keyword: {keyword}")
                return None
            
            content = response.text
            start_idx = content.find('{')
            if start_idx == -1:
                print(f"[-] No JSON found for keyword: {keyword}")
                return None
            
            clean_content = content[start_idx:].strip()
            data = json.loads(clean_content)
            
            total_count = data.get("result", {}).get("totalCount", 0)
            return total_count
        except Exception as e:
            print(f"[-] Error fetching count for '{keyword}': {e}")
            return None

    def run(self, keywords, days=180, start_date=None, end_date=None, output_file="mara_counts.csv"):
        results = []
        
        if start_date and end_date:
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            # Calculate start and end dates (up to yesterday)
            end_date_dt = datetime.now() - timedelta(days=1)
            start_date_dt = end_date_dt - timedelta(days=days)
        
        print(f"[+] Starting daily aggregation for {len(keywords)} keywords")
        print(f"[+] Period: {start_date_dt.strftime('%Y-%m-%d')} ~ {end_date_dt.strftime('%Y-%m-%d')}")
        
        current_dt = start_date_dt
        while current_dt <= end_date_dt:
            date_str = current_dt.strftime("%Y-%m-%d")
            print(f"\n[+] Date: {date_str}")
            
            for keyword in keywords:
                print(f"  [+] Fetching: {keyword}...", end="", flush=True)
                count = self.get_blog_count(keyword, start_date=date_str, end_date=date_str)
                
                if count is not None:
                    print(f" {count:,}건")
                    data_row = {
                        "date": date_str,
                        "keyword": keyword,
                        "total_count": count
                    }
                    results.append(data_row)
                    
                    # DB 저장 시도
                    if self.db:
                        self.db.insert_blog_trend(data_row)
                else:
                    print(" Failed")
                
                # Policy compliance: delay between requests
                time.sleep(0.5)
            
            # Save results daily to CSV to avoid data loss
            if results:
                df = pd.DataFrame(results)
                if os.path.exists(output_file):
                    df.to_csv(output_file, mode='a', index=False, header=False, encoding='utf-8-sig')
                else:
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                results = [] # Clear results after saving
                
            current_dt += timedelta(days=1)
            
        print(f"\n[+] Successfully completed daily aggregation. Results saved to {output_file}")

if __name__ == "__main__":
    # Sample keywords
    target_keywords = ["마라샹궈"]
    
    crawler = NaverBlogCrawler()
    # CSV 경로 설정 (실행 위치에 따라 조정 필요)
    csv_path = "mara_counts.csv"
    crawler.run(target_keywords, start_date="2018-01-01", end_date="2020-12-31", output_file=csv_path)
