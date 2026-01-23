"""
네이버 뉴스 검색 및 URL 수집 모듈
정적 크롤링 우선, 필요시 네이버 검색 API 사용
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote
import time
from config.settings import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, MAX_NEWS_COUNT


class NaverNewsSearcher:
    """네이버 뉴스 검색 및 URL 수집 클래스"""
    
    def __init__(self):
        """초기화"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.use_api = bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)
        
        if self.use_api:
            print("✅ 네이버 검색 API 사용")
        else:
            print("✅ 웹 크롤링 방식 사용 (API 미설정)")
    
    def search_news_by_api(self, keyword: str, max_count: int = MAX_NEWS_COUNT) -> List[Dict]:
        """
        네이버 검색 API를 통한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            max_count: 최대 수집 개수
            
        Returns:
            뉴스 정보 리스트 [{'title', 'link', 'description', 'pubDate'}]
        """
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }
        params = {
            'query': keyword,
            'display': min(max_count, 100),  # API 최대 100개
            'sort': 'date'  # 최신순
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            news_list = []
            for item in data.get('items', []):
                # 네이버 뉴스만 필터링 (댓글이 있는 뉴스)
                if 'news.naver.com' in item['link']:
                    news_list.append({
                        'title': self._clean_html_tags(item['title']),
                        'link': item['link'],
                        'description': self._clean_html_tags(item['description']),
                        'pubDate': item['pubDate']
                    })
            
            print(f"✅ API로 {len(news_list)}개 뉴스 URL 수집 완료")
            return news_list
            
        except Exception as e:
            print(f"❌ API 검색 실패: {e}")
            return []
    
    def search_news_by_crawling(self, keyword: str, max_count: int = MAX_NEWS_COUNT) -> List[Dict]:
        """
        웹 크롤링을 통한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            max_count: 최대 수집 개수
            
        Returns:
            뉴스 정보 리스트
        """
        encoded_keyword = quote(keyword)
        news_list = []
        
        # 네이버 뉴스 검색 결과 페이지 크롤링
        for start in range(1, max_count + 1, 10):
            url = f"https://search.naver.com/search.naver?where=news&query={encoded_keyword}&start={start}"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 뉴스 항목 찾기
                news_items = soup.select('div.news_area')
                
                for item in news_items:
                    if len(news_list) >= max_count:
                        break
                    
                    # 제목과 링크 추출
                    title_elem = item.select_one('a.news_tit')
                    if not title_elem:
                        continue
                    
                    link = title_elem.get('href', '')
                    
                    # 네이버 뉴스만 필터링
                    if 'news.naver.com' not in link:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 요약 추출
                    desc_elem = item.select_one('div.news_dsc')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'pubDate': ''  # 크롤링에서는 날짜 정보 제한적
                    })
                
                if len(news_list) >= max_count:
                    break
                
                time.sleep(0.5)  # 요청 간격 조절
                
            except Exception as e:
                print(f"❌ 페이지 크롤링 실패 (start={start}): {e}")
                continue
        
        print(f"✅ 크롤링으로 {len(news_list)}개 뉴스 URL 수집 완료")
        return news_list
    
    def search_news(self, keyword: str, max_count: int = MAX_NEWS_COUNT) -> List[Dict]:
        """
        뉴스 검색 (API 우선, 실패시 크롤링)
        
        Args:
            keyword: 검색 키워드
            max_count: 최대 수집 개수
            
        Returns:
            뉴스 정보 리스트
        """
        print(f"🔍 '{keyword}' 키워드로 뉴스 검색 중...")
        
        if self.use_api:
            news_list = self.search_news_by_api(keyword, max_count)
            if news_list:
                return news_list
            print("⚠️  API 검색 실패, 크롤링으로 전환")
        
        return self.search_news_by_crawling(keyword, max_count)
    
    @staticmethod
    def _clean_html_tags(text: str) -> str:
        """HTML 태그 제거"""
        return BeautifulSoup(text, 'html.parser').get_text()


if __name__ == "__main__":
    # 테스트
    searcher = NaverNewsSearcher()
    results = searcher.search_news("AI", max_count=5)
    
    for i, news in enumerate(results, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   URL: {news['link']}")
