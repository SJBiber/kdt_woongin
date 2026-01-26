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
                
                # First, find and click the sidebar item to scroll/activate the section
                sidebar_item = page.locator('button').filter(has_text=re.compile(f"^{category_name}$")).first
                if await sidebar_item.count() > 0:
                    print(f"Clicking sidebar item: {category_name}")
                    await sidebar_item.click()
                    await asyncio.sleep(1)

                # Now find the header button in the content area that leads to the full page.
                # Usually contains the name and a chevron ">".
                header_link = page.locator('button').filter(has_text=re.compile(f"^{category_name}.*>")).first
                
                if await header_link.count() == 0:
                    # Fallback: look for any button that starts with category name and likely navigates
                    header_link = page.locator('button').filter(has_text=re.compile(f"^{category_name}")).filter(has=page.locator('svg')).first
                
                if await header_link.count() > 0:
                    print(f"Clicking main category header link for: {category_name}")
                    await header_link.click()
                    await asyncio.sleep(3)
                    clicked = True
                else:
                    # Final fallback: search for text and try to find a clickable parent or siblings
                    print("Heading link not found with specific pattern, trying generic text search...")
                    category_locators = page.locator(f"//p[text()='{category_name}'] | //span[text()='{category_name}'] | //button[contains(., '{category_name}')]")
                    count = await category_locators.count()
                    if count > 0:
                        # Pick the one that changes the URL
                        for i in range(count):
                            target = category_locators.nth(i)
                            old_url = page.url
                            await target.click()
                            await asyncio.sleep(2)
                            if page.url != old_url:
                                clicked = True
                                print(f"Successfully navigated via fallback to: {page.url}")
                                break
                
                if not clicked:
                    print(f"Category '{category_name}' navigation failed. Current URL: {page.url}")
                    if "/categories/" in page.url:
                        print("Stopping because we are still on categories page.")
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
                # Primary: H1 with semantic classes
                name_sel = page.locator('h1[class*="BODY"], h1[class*="css-"], h1').first
                if await name_sel.count() > 0:
                    product_name = (await name_sel.text_content()).strip()
                else:
                    # Fallback to OG title
                    og_title = await page.locator("meta[property='og:title']").get_attribute("content")
                    if og_title:
                        product_name = og_title.split(" - ")[0].strip()
            except:
                pass

            # 2. 브랜드명
            brand_name = "Unknown"
            # Updated selectors based on current site structure
            brand_sel = page.locator('a[class*="e1jx89fy1"], h2[class*="e1qy47wz6"], [class*="StoreName"], p[class*="brand"]').first
            if await brand_sel.count() > 0:
                brand_name = (await brand_sel.text_content()).strip()

            # 3. 가격
            final_price = 0
            # Target specific price classes
            price_sel = page.locator('[class*="e1sus6ys1"], span[class*="SalesPrice"], span[class*="Price"].bold, div[class*="SalesPrice"]').first
            if await price_sel.count() > 0:
                text = await price_sel.text_content()
                match = re.search(r"[\d,]+", text)
                if match:
                    final_price = int(match.group().replace(",", ""))

            # 4. 리뷰 정보 (Count & Rating)
            review_count = 0
            rating_average = 0.0
            
            # Review count summary near title/rating
            rev_cnt_sel = page.locator('[class*="evpy3qu0"], [class*="review_count"], a[href*="/review"] span').first
            if await rev_cnt_sel.count() > 0:
                text = await rev_cnt_sel.text_content()
                match = re.search(r"[\d,]+", text)
                if match:
                    review_count = int(match.group().replace(",", ""))

            # Rating
            rating_sel = page.locator('[class*="Rating"], span[class*="rating_score"]').first
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
            print(f"Collecting reviews for {product_name}...")
            rev_tab = page.locator('button:has-text("리뷰"), a:has-text("리뷰")').first
            if await rev_tab.count() > 0:
                await rev_tab.click()
                await asyncio.sleep(2)
                # Scroll to ensure lazy items load
                for _ in range(3):
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(0.5)

            reviews = []
            # Updated selectors for review items container and content
            # data-review-feed-index is a very reliable selector for Zigzag reviews
            review_els = await page.locator('div[data-review-feed-index], div[class*="ReviewItem"], div[data-custom-ta-key*="PDP_REVIEW_CELL"], li[class*="ReviewItem"]').all()
            print(f"Found {len(review_els)} potential review elements.")
            
            for item in review_els[:20]:
                content = ""
                rating = 5
                
                # Content: span[class*="ebrcgb90"] is highly specific for review text
                content_el = item.locator('span[class*="ebrcgb90"], span[class*="zds4_"], div[class*="BODY"], div[class*="content"], p[class*="text"]').first
                 if await content_el.count() > 0:
                    content = (await content_el.text_content()).strip()
                
                # Rating: aria-label contains star count
                ## 라뷰별 별점 데이터는 그림으로 수치화 되어 있음 이거 한번 스크립트에서 확인 해봐야함ss
                star_el = item.locator('[aria-label*="별점"], [class*="Rating"], [class*="star"]').first
                if await star_el.count() > 0:
                    label = await star_el.get_attribute("aria-label")
                    if label:
                        match = re.search(r"\d", label)
                        if match: rating = int(match.group())
                
                if content:
                    reviews.append({"content": content, "rating": rating})

            if reviews:
                self.db.save_reviews(product_id, reviews)
                print(f"Success: Collected {len(reviews)} reviews.")
            else:
                print("No reviews found or failed to parse reviews.")

        finally:
            await page.close()




