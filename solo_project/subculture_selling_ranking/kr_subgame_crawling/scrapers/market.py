from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

class MarketScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def get_google_play_rankings(self, limit=5):
        """
        [긴급 수정] 모바일 인덱스(Mobile Index) 실시간 순위 페이지를 사용하여 
        구글 플레이 매출 순위를 확실하게 추출합니다.
        """
        # 모바일인덱스 구글플레이 매출 순위 페이지
        url = "https://www.mobileindex.com/mi-chart/top-grossing/google"
        
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 1000},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page() 
            
            try:
                print(f"모바일인덱스 실시간 차트 접속 중...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # 차트 데이터 로딩 대기
                page.wait_for_selector('table', timeout=20000)
                time.sleep(2) # 데이터 렌더링 추가 대기

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 모바일인덱스 차트에서 게임 제목 추출
                # 보통 'list-app-name' 또는 특정 구조의 span 내부에 있음
                app_names = soup.select('.app-name') or soup.select('.list-app-name') or soup.select('span.name')
                
                for idx, name_elem in enumerate(app_names):
                    if len(results) >= limit:
                        break
                    
                    game_title = name_elem.get_text(strip=True)
                    if game_title:
                        results.append({
                            "rank": len(results) + 1,
                            "title": game_title,
                            "date": time.strftime("%Y-%m-%d")
                        })
                
                # 만약 위 셀렉터가 실패할 경우 table row 분석
                if not results:
                    rows = soup.find_all('tr')
                    for row in rows:
                        tds = row.find_all('td')
                        if len(tds) > 1:
                            # 텍스트가 있는 셀을 하나씩 확인
                            for td in tds:
                                txt = td.get_text(strip=True)
                                if txt and 2 <= len(txt) <= 30:
                                    # 순위 숫자는 제외
                                    if txt.isdigit(): continue
                                    if txt not in [r['title'] for r in results]:
                                        results.append({
                                            "rank": len(results) + 1,
                                            "title": txt,
                                            "date": time.strftime("%Y-%m-%d")
                                        })
                                        break
                        if len(results) >= limit: break

            except Exception as e:
                print(f"모바일인덱스 스크래핑 중 오류: {e}")
            finally:
                browser.close()
        
        return results

if __name__ == "__main__":
    scraper = MarketScraper(headless=True)
    ranks = scraper.get_google_play_rankings(limit=5)
    print("\n[모바일인덱스 확인 결과]")
    for r in ranks:
        print(f"{r['rank']}위: {r['title']}")
