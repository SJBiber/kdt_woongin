import os
import requests
import json
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class TrendScraper:
    def __init__(self):
        self.naver_client_id = os.environ.get("NAVER_CLIENT_ID")
        self.naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET")
        self.pytrends = TrendReq(hl='ko-KR', tz=540) # 한국 시간대 설정

    def get_naver_trend(self, keyword: str, days=7):
        """
        네이버 데이터랩 API를 사용하여 검색 트렌드를 가져옵니다.
        """
        url = "https://openapi.naver.com/v1/datalab/search"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "date",
            "keywordGroups": [
                {"groupName": keyword, "keywords": [keyword]}
            ]
        }

        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            data = response.json()
            return data["results"][0]["data"]
        except Exception as e:
            print(f"네이버 트렌드 조회 오류 ({keyword}): {e}")
            return None

    def get_google_trend(self, keyword: str, timeframe='now 7-d'):
        """
        Google Trends 데이터를 가져옵니다.
        """
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='KR')
            data = self.pytrends.interest_over_time()
            if not data.empty:
                return data[keyword].to_dict()
            return None
        except Exception as e:
            print(f"구글 트렌드 조회 오류 ({keyword}): {e}")
            return None

if __name__ == "__main__":
    # 테스트 실행
    scraper = TrendScraper()
    print("네이버 결과:", scraper.get_naver_trend("블루 아카이브"))
    print("구글 결과:", scraper.get_google_trend("블루 아카이브"))
