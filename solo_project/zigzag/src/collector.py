import asyncio
import random
import re
from playwright.async_api import async_playwright
from src.database import DatabaseManager

class ZigzagCollector:
    def __init__(self):
        self.db = DatabaseManager()
        self.base_url = "https://zigzag.kr"

    async def run(self, category_name: str):
        async with async_playwright() as p:
            # Headless=True for more stable execution in CLI, but keeping False for now to monitor
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # 1. 메인 페이지 접속
                print(f"Navigating to {self.base_url}...")
                await page.goto(self.base_url, timeout=60000)
                await page.wait_for_load_state("networkidle")

                # 2. 카테고리 메뉴 진입
                print("Clicking Category menu...")
                # Try multiple selectors for the category link
                cat_selectors = ['a[href="/categories"]', 'a[href*="/category"]', 'button:has-text("카테고리")']
                for sel in cat_selectors:
                    if await page.locator(sel).count() > 0:
                        await page.click(sel)
                        break
                else:
                    # Fallback to direct navigation
                    await page.goto(f"{self.base_url}/categories")
                
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(3)
                
                # 3. 대항목 클릭
                print(f"Finding category item: {category_name}")
                # Target items that are likely to be the main navigation buttons (avoiding sidebar that only scrolls)
                # We look for all matching items and try to click the one that navigates.
                category_locators = page.locator(f"//p[text()='{category_name}'] | //span[text()='{category_name}'] | //button[contains(., '{category_name}')]")
                count = await category_locators.count()
                
                clicked = False
                if count > 0:
                    # In Zigzag, the sidebar items usually appear first. The main content items follow.
                    # We try to click the last one first as it's more likely to be the content link.
                    for i in reversed(range(count)):
                        target = category_locators.nth(i)
                        old_url = page.url
                        await target.click()
                        await asyncio.sleep(3)
                        if page.url != old_url:
                            clicked = True
                            print(f"Successfully navigated to: {page.url}")
                            break
                
                if not clicked:
                    print(f"Category '{category_name}' navigation failed or not found. Current URL: {page.url}")
                    # If we are already on a relevant page, continue. If not, stop.
                    if category_name not in await page.title() and "/categories/" not in page.url:
                        return

                # 4. 정렬: 인기순
                print("Setting sort order to Popular (인기순)...")
                # Ensure we are looking for the sort button on the product list page
                sort_btn = page.locator('button').filter(has_text=re.compile(r"순$|인기|추천|랭킹")).first
                if await sort_btn.count() > 0:
                    await sort_btn.click()
                    await asyncio.sleep(1)
                    pop_opt = page.locator('//p[text()="인기순"] | //span[text()="인기순"] | //div[text()="인기순"] | //li[contains(., "인기순")]').first
                    if await pop_opt.count() > 0:
                        await pop_opt.click()
                        await asyncio.sleep(2)

                # 5. 상품 리스트 확보 (무한 스크롤)
                print("Scrolling to load products...")
                for _ in range(3):
                    await page.mouse.wheel(0, 1500)
                    await asyncio.sleep(2)

                # 상품 카드 식별 (Verified selector: a[class*="product-card-link"])
                # Also fallback to general product link pattern
                product_links = await page.locator('a[class*="product-card-link"], a[href*="/catalog/products/"]').all()
                unique_urls = []
                seen_urls = set()
                
                for link in product_links:
                    url = await link.get_attribute("href")
                    if url:
                        full_url = self.base_url + url if url.startswith("/") else url
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            unique_urls.append(full_url)
                
                print(f"Found {len(unique_urls)} unique products.")
                target_urls = unique_urls[:20]

                # 6. 상세 페이지 순회
                for idx, prod_url in enumerate(target_urls):
                    print(f"[{idx+1}/{len(target_urls)}] Scraping {prod_url}...")
                    try:
                        await self._scrape_product_detail(context, prod_url, category_name)
                    except Exception as e:
                        print(f"Failed to scrape {prod_url}: {e}")
                    
                    await asyncio.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"Critical Error: {e}")
            finally:
                await browser.close()

    async def _scrape_product_detail(self, context, url, category):
        page = await context.new_page()
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3) # Wait for AJAX

            # 1. 상품명
            product_name = "Unknown"
            try:
                # OpenGraph title is usually clean: "Brand Name Product Name - Zigzag"
                og_title = await page.locator("meta[property='og:title']").get_attribute("content")
                if og_title:
                    product_name = og_title.split(" - ")[0].strip()
            except:
                pass

            # 2. 브랜드명
            brand_name = "Unknown"
            # Brand is often linked to /store/ or has specific brand classes
            brand_sel = page.locator('p[class*="brand"], a[href*="/store/"], div[class*="StoreName"]').first
            if await brand_sel.count() > 0:
                brand_name = (await brand_sel.text_content()).strip()

            # 3. 가격
            final_price = 0
            # Look for elements with "SalesPrice" or specific bold price classes
            price_sel = page.locator('span[class*="SalesPrice"], span[class*="Price"].bold, div[class*="SalesPrice"]').first
            if await price_sel.count() > 0:
                text = await price_sel.text_content()
                match = re.search(r"[\d,]+", text)
                if match:
                    final_price = int(match.group().replace(",", ""))

            # 4. 리뷰 정보 (Count & Rating)
            review_count = 0
            rating_average = 0.0
            
            # Review count often in the tab meta or summary
            rev_cnt_sel = page.locator('span[class*="review_count"], a[href*="/review"] span').first
            if await rev_cnt_sel.count() > 0:
                text = await rev_cnt_sel.text_content()
                match = re.search(r"[\d,]+", text)
                if match:
                    review_count = int(match.group().replace(",", ""))

            # Rating
            rating_sel = page.locator('span[class*="rating_score"], div[class*="Rating"]').first
            if await rating_sel.count() > 0:
                text = await rating_sel.text_content()
                match = re.search(r"(\d+(\.\d+)?)", text)
                if match:
                    rating_average = float(match.group(1))

            # 5. 이미지
            image_url = ""
            try:
                image_url = await page.locator("meta[property='og:image']").get_attribute("content")
            except:
                pass

            product_data = {
                "category_major": category,
                "brand_name": brand_name,
                "product_name": product_name,
                "final_price": final_price,
                "review_count": review_count,
                "rating_average": rating_average,
                "image_url": image_url,
                "product_url": url
            }
            
            product_id = self.db.save_product(product_data)
            print(f"Saved: {product_name[:30]}... | Price: {final_price} | Reviews: {review_count}")

            # 6. 리뷰 수집 (최대 20개)
            # Try to click review tab if it's not active
            rev_tab = page.locator('button:has-text("리뷰"), a:has-text("리뷰")').first
            if await rev_tab.count() > 0:
                await rev_tab.click()
                await asyncio.sleep(2)

            reviews = []
            # Updated selector for review items based on analysis
            review_els = await page.locator('div[data-custom-ta-key*="PDP_REVIEW_CELL"], div[class*="ReviewItem"]').all()
            
            for item in review_els[:20]:
                content = ""
                rating = 5
                
                # Content: Looking for BODY_14 REGULAR or similar semantic classes
                content_el = item.locator('div[class*="BODY"], div[class*="content"], p[class*="text"]').first
                if await content_el.count() > 0:
                    content = (await content_el.text_content()).strip()
                
                # Rating: Usually an aria-label like "별점 5점"
                star_el = item.locator('div[aria-label*="별점"]').first
                if await star_el.count() > 0:
                    label = await star_el.get_attribute("aria-label")
                    if label:
                        match = re.search(r"\d", label)
                        if match: rating = int(match.group())
                
                if content:
                    reviews.append({"content": content, "rating": rating})

            if reviews:
                self.db.save_reviews(product_id, reviews)

        finally:
            await page.close()




