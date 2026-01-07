from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

class CommunityScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def get_arcalive_best(self, channel_name: str):
        """
        [일시 중단] 현재 커뮤니티 스크래핑은 건너뜁니다.
        """
        # print(f"커뮤니티 조사는 현재 비활성화 상태입니다 ({channel_name})")
        return []

    # 기존 Playwright 로직은 주석 처리 보존
    """
    def get_arcalive_best_v2(self, channel_name: str):
        url = f"https://arca.live/b/{channel_name}?mode=best"
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle")
                page.wait_for_selector('.article-list', timeout=10000)
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                articles = soup.select('.article-list .vrow-default')
                for article in articles:
                    title_tag = article.select_one('.title')
                    if not title_tag: continue
                    title = title_tag.get_text(strip=True)
                    comment_tag = article.select_one('.comment-count')
                    comment_count = comment_tag.get_text(strip=True).strip('[]') if comment_tag else "0"
                    results.append({
                        "channel": channel_name,
                        "title": title,
                        "comment_count": comment_count,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
            except Exception as e:
                print(f"아카라이브 스크래핑 오류: {e}")
            finally:
                browser.close()
        return results
    """

if __name__ == "__main__":
    scraper = CommunityScraper()
    print("커뮤니티 스크래퍼 (비활성 모드)")
