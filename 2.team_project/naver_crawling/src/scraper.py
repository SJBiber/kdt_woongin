import requests
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from pathlib import Path

# 설정 로드 - config/.env
config_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

class NaverScraper:
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.url = "https://openapi.naver.com/v1/search/blog.json"


    def fetch_all_180_days(self, keyword, days=180):
        """
        180일 동안의 데이터를 수집하기 위해, 
        단순 1000개 수집이 아닌 날짜별 수집 전략을 사용합니다.
        """
        all_items = []
        # 네이버 블로그 Open API는 특정 날짜 범위를 지정하는 파라미터가 없으므로
        # 날짜순(sort=date)으로 최대한 많이(1000개) 가져오는 과정을 반복하거나
        # 검색 시스템의 한계를 인정하고 1000개 내에서 처리해야 합니다.
        
        # 하지만 유저가 '날짜별 검색 로직'을 원하므로, 
        # 검색어에 날짜를 포함하여 해당 날짜의 total 개수를 추정하는 방식으로 구현합니다.
        # 예: "두바이 초코 쿠키 2024.01.01"
        
        daily_counts = []
        end_date = datetime.now() - timedelta(days=1)
        
        print(f"[{keyword}] 180일치 날짜별 데이터 추정 시작...")
        
        for i in range(days):
            target_date = end_date - timedelta(days=i)
            # 네이버 블로그 검색에서 "키워드" + "YYYY.MM.DD" 조합은 해당 날짜에 작성된 글을 찾는 데 효과적입니다.
            date_query = target_date.strftime("%Y.%m.%d")
            query = f'"{keyword}" {date_query}'
            
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            params = {"query": query, "display": 1}
            
            try:
                res = requests.get(self.url, headers=headers, params=params)
                if res.status_code == 200:
                    total = res.json().get("total", 0)
                    daily_counts.append({
                        "keyword": keyword,
                        "target_date": target_date.strftime("%Y-%m-%d"),
                        "post_count": total
                    })
                    print(f"  - {target_date.strftime('%Y-%m-%d')}: {total}건")
                else:
                    print(f"  - {target_date.strftime('%Y-%m-%d')}: 요청 실패")
                
                time.sleep(0.1) # 속도 제한
            except Exception as e:
                print(f"  - {target_date.strftime('%Y-%m-%d')}: 오류 {e}")
                
        return daily_counts
