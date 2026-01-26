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
        네이버 검색 API를 통한 뉴스 검색 (페이징 지원)
        """
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }
        
        news_list = []
        display = 100
        # API 최대 허용 start 값은 1000입니다.
        for start in range(1, min(max_count, 1001), display):
            params = {
                'query': keyword,
                'display': min(display, max_count - len(news_list)),
                'start': start,
                'sort': 'date'
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                items = data.get('items', [])
                if not items:
                    break
                    
                for item in items:
                    news_list.append({
                        'title': self._clean_html_tags(item['title']),
                        'link': item['link'],
                        'description': self._clean_html_tags(item['description']),
                        'pubDate': item['pubDate'],
                        'originallink': item.get('originallink', item['link'])
                    })
                
                if len(news_list) >= max_count:
                    break
                    
                time.sleep(0.1) # 짧은 지연
                
            except Exception as e:
                print(f"❌ API 검색 중 오류 (start={start}): {e}")
                break
        
        print(f"✅ API로 {len(news_list)}개 뉴스 URL 수집 완료")
        return news_list
    
    def search_news_by_crawling(self, keyword: str, max_count: int = MAX_NEWS_COUNT, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        웹 크롤링을 통한 뉴스 검색 (날짜 필터링 지원)
        
        Args:
            keyword: 검색 키워드
            max_count: 최대 수집 개수
            start_date: 시작일 (YYYY.MM.DD 형식)
            end_date: 종료일 (YYYY.MM.DD 형식)
        """
        encoded_keyword = quote(keyword)
        news_list = []
        
        # 날짜 필터링 파라미터 구성 (확인된 네이버 뉴스 웹 규격)
        date_query = ""
        if end_date:
            if not start_date:
                start_date = "2024.12.01" # 최근 한 달 정도 (수정)
            
            # YYYY.MM.DD -> YYYYMMDD 변환 (점 제거 필수)
            s_num = start_date.replace(".", "").strip()
            e_num = end_date.replace(".", "").strip()
            
            # 네이버 웹에서 추출한 가장 확실한 파라미터 조합
            # pd=3: 기간 설정 모드
            # ds/de: 검색창 표시용
            # nso: 검색 엔진 필터링용 (so:dd는 최신순, p:from...to... 는 기간)
            date_query = f"&pd=3&ds={start_date}&de={end_date}&nso=so:dd,p:from{s_num}to{e_num},a:all"
            
        print(f"🕵️ 기간 검색 활성: {start_date} ~ {end_date}")
        
        for start in range(1, max_count + 1, 10):
            # nso 기반 URL (sort=1 같은 다른 정렬 파라미터와 충돌 방지)
            url = f"https://search.naver.com/search.naver?where=news&query={encoded_keyword}&start={start}{date_query}"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = soup.select('div.news_area')
                if not news_items:
                    print("⚠️ 더 이상 발견된 뉴스가 없습니다.")
                    break
                
                for item in news_items:
                    if len(news_list) >= max_count:
                        break
                    
                    title_elem = item.select_one('a.news_tit')
                    if not title_elem:
                        continue
                    
                    link = title_elem.get('href', '')
                    title = title_elem.get_text(strip=True)
                    
                    desc_elem = item.select_one('div.news_dsc')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'pubDate': '' 
                    })
                
                if len(news_list) % 100 == 0:
                    print(f"⏳ 현재 {len(news_list)}개 수집 중...")
                
                if len(news_list) >= max_count:
                    break
                
                # 대량 크롤링 시 차단 방지를 위해 지연 시간 조절
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ 페이지 크롤링 실패 (start={start}): {e}")
                break
        
        print(f"✅ 크롤링으로 {len(news_list)}개 뉴스 수집 완료")
        return news_list
    
    def search_news(self, keyword: str, max_count: int = MAX_NEWS_COUNT, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        뉴스 검색 (API와 크롤링 결과 결합, 날짜 필터링 지원)
        """
        # 종료일만 있고 시작일이 없으면 검색이 안되는 경우를 방지하기 위해 임의의 시작일 설정
        if end_date and not start_date:
            start_date = "2025.01.01" # 충분히 과거 시점
            
        print(f"🔍 '{keyword}' 키워드로 뉴스 검색 중 (목표: {max_count}개)...")
        
        final_list = []
        
        # 1. 특정 기간 검색이 아니고 API 사용 가능할 때 API 검색 우선 시도
        if not (start_date or end_date) and self.use_api:
            api_results = self.search_news_by_api(keyword, max_count)
            final_list.extend(api_results)
        
        # 2. 기간 검색이거나 목표치에 도달하지 못했다면 크롤링으로 보충/검색
        if len(final_list) < max_count:
            if final_list:
                print(f"⚠️  API 수집 완료 ({len(final_list)}개), 부족한 부분을 크롤링으로 보충합니다.")
            
            existing_links = {item['link'] for item in final_list}
            
            # 크롤링 수행 (날짜 필터링 포함)
            crawl_results = self.search_news_by_crawling(keyword, max_count, start_date, end_date)
            
            for item in crawl_results:
                if item['link'] not in existing_links:
                    final_list.append(item)
                    existing_links.add(item['link'])
                
                if len(final_list) >= max_count:
                    break
        
        print(f"✅ 최종적으로 {len(final_list)}개 뉴스 URL을 확보했습니다.")
        return final_list[:max_count]
    
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
