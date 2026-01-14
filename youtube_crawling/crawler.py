import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from tqdm import tqdm
import sys
import io

# 터미널 한글 깨짐 방지 (Windows 환경)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

class YouTubeCrawler:
    def __init__(self):
        self.base_url = "https://www.youtube.com"
        
    async def get_video_urls(self, keyword, max_videos=5):
        """키워드로 검색하여 영상 URL 리스트를 가져옵니다."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            search_url = f"{self.base_url}/results?search_query={keyword}"
            print(f"[*] 검색 시작: {search_url}")
            await page.goto(search_url)
            await page.wait_for_selector("ytd-video-renderer")
            
            # 영상 링크 추출
            video_links = await page.query_selector_all("ytd-video-renderer #video-title")
            urls = []
            for link in video_links[:max_videos]:
                href = await link.get_attribute("href")
                if href:
                    urls.append(f"{self.base_url}{href}")
            
            await browser.close()
            return urls

    async def get_comments(self, video_url, max_comments=50):
        """특정 영상의 댓글을 수집합니다."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"[*] 영상 접속: {video_url}")
            await page.goto(video_url)
            
            # 페이지 로딩 및 댓글 섹션으로 스크롤
            await page.evaluate("window.scrollTo(0, 600)")
            try:
                await page.wait_for_selector("#comments", timeout=10000)
            except:
                print("[!] 댓글 섹션을 찾을 수 없습니다.")
                await browser.close()
                return []

            comments = []
            pbar = tqdm(total=max_comments, desc="댓글 수집 중")
            
            while len(comments) < max_comments:
                # 스크롤 다운하여 댓글 로딩
                await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                await asyncio.sleep(2) # 로딩 대기
                
                comment_elems = await page.query_selector_all("#content-text")
                for elem in comment_elems[len(comments):]:
                    text = await elem.inner_text()
                    if text and len(comments) < max_comments:
                        comments.append(text)
                        pbar.update(1)
                
                # 더 이상 로딩할 댓글이 없는지 체크 (간단한 로직)
                if len(comment_elems) == len(comments) and len(comments) > 0:
                    break
            
            pbar.close()
            await browser.close()
            return comments

async def main():
    crawler = YouTubeCrawler()
    keyword = "흑백요리사" # 테스트 키워드
    
    # 1. 영상 URL 가져오기
    urls = await crawler.get_video_urls(keyword, max_videos=2)
    print(f"[+] 수집된 영상 개수: {len(urls)}")
    
    # 2. 첫 번째 영상에서 댓글 수집 테스트
    if urls:
        comments = await crawler.get_comments(urls[0], max_comments=20)
        df = pd.DataFrame(comments, columns=["comment"])
        df.to_csv("youtube_crawling/test_comments.csv", index=False, encoding="utf-8-sig")
        print(f"[+] {len(comments)}개의 댓글이 test_comments.csv에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
