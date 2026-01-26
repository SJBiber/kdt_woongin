import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import quote
import os

class NaverBlogCrawler:
    def __init__(self):
        self.url = "https://section.blog.naver.com/ajax/SearchList.naver"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }

    def get_blog_count(self, keyword, start_date="", end_date=""):
        """
        특정 기간 동안의 블로그 포스팅 수를 가져옵니다.
        """
        params = {
            "countPerPage": "7",
            "currentPage": "1",
            "startDate": start_date,
            "endDate": end_date,
            "keyword": keyword,
            "orderBy": "sim"
        }
        
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
