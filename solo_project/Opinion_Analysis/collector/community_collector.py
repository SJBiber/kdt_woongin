import time
import logging
import hashlib
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class YouTubeCommunityCollector:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def _parse_likes(self, likes_text):
        if not likes_text or likes_text.strip() == "":
            return 0
        
        likes_text = likes_text.strip().replace(",", "")
        try:
            if '만' in likes_text:
                return int(float(likes_text.replace('만', '')) * 10000)
            if '천' in likes_text:
                return int(float(likes_text.replace('천', '')) * 1000)
            if 'K' in likes_text.upper():
                return int(float(likes_text.upper().replace('K', '')) * 1000)
            if 'M' in likes_text.upper():
                return int(float(likes_text.upper().replace('M', '')) * 1000000)
            
            digits = re.findall(r'\d+\.?\d*', likes_text)
            if digits:
                return int(float(digits[0]))
            return 0
        except:
            return 0

    def _format_date(self, time_str):
        """'1일 전', '2주 전' 등을 실제 ISO 날짜로 변환"""
        if not time_str:
            return datetime.now().isoformat()
            
        now = datetime.now()
        # 숫자 추출
        match = re.search(r'(\d+)', time_str)
        if not match:
            return now.isoformat()
            
        value = int(match.group(1))
        
        # 단위별 역산 (한국어/영어 모두 대응)
        if any(x in time_str for x in ['초', 'second']):
            delta = timedelta(seconds=value)
        elif any(x in time_str for x in ['분', 'minute']):
            delta = timedelta(minutes=value)
        elif any(x in time_str for x in ['시간', 'hour']):
            delta = timedelta(hours=value)
        elif any(x in time_str for x in ['일', 'day']):
            delta = timedelta(days=value)
        elif any(x in time_str for x in ['주', 'week']):
            delta = timedelta(weeks=value)
        elif any(x in time_str for x in ['달', '월', 'month']):
            delta = timedelta(days=value * 30)
        elif any(x in time_str for x in ['년', 'year']):
            delta = timedelta(days=value * 365)
        else:
            delta = timedelta(0)
            
        target_date = now - delta
        return target_date.isoformat()

    def fetch_comments(self, url, limit=100):
        logger.info(f"Opening YouTube Community Post: {url}")
        self.driver.get(url)
        time.sleep(5) 

        collected_data = []
        seen_ids = set() # 중복 방지를 위한 셋
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        video_id = url.split("/post/")[-1].split("?")[0]

        while len(collected_data) < limit:
            comment_threads = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
            
            # 스크롤 시마다 전체 요소를 다시 확인하되, 이미 수집한 ID는 건너뜀
            for thread in comment_threads:
                if len(collected_data) >= limit:
                    break
                
                try:
                    # 데이터 추출 시도
                    author_elem = thread.find_element(By.CSS_SELECTOR, "#author-text")
                    author = author_elem.text.strip()
                    content = thread.find_element(By.CSS_SELECTOR, "#content-text").text.strip()
                    likes_text = thread.find_element(By.CSS_SELECTOR, "#vote-count-middle").text.strip()
                    likes = self._parse_likes(likes_text)

                    # 고유 ID 및 링크 추출
                    try:
                        link_element = thread.find_element(By.CSS_SELECTOR, "a#thumbnail-author")
                        full_id = link_element.get_attribute("href").split("lc=")[-1]
                        comment_id = full_id if full_id else f"comm_{video_id}_{int(time.time() * 1000)}"
                    except:
                        hash_input = f"{author}_{content[:50]}".encode('utf-8')
                        comment_id = f"hash_{hashlib.md5(hash_input).hexdigest()}"

                    # 날짜 텍스트 추출
                    try:
                        time_text = thread.find_element(By.CSS_SELECTOR, ".published-time-text").text.strip()
                    except:
                        time_text = ""

                    # 이번 수집 세션 내에서의 중복 체크
                    if comment_id not in seen_ids:
                        collected_data.append({
                            "comment_id": comment_id,
                            "video_id": video_id,
                            "author": author,
                            "content": content,
                            "likes": likes,
                            "published_at": self._format_date(time_text)
                        })
                        seen_ids.add(comment_id)
                        
                        if len(collected_data) % 20 == 0:
                            logger.info(f"Collected {len(collected_data)} community comments...")

                except Exception as e:
                    continue

            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)
            
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                time.sleep(2)
                if self.driver.execute_script("return document.documentElement.scrollHeight") == last_height:
                    break
            last_height = new_height

        logger.info(f"Total unique collected: {len(collected_data)} community comments.")
        return collected_data

    def close(self):
        self.driver.quit()
