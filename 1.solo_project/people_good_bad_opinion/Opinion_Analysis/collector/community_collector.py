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
        """'1일 전', '2주 전', '2024. 1. 20.' 등을 실제 ISO 날짜로 변환"""
        if not time_str:
            return datetime.now().isoformat()
            
        now = datetime.now()
        
        # '방금', 'just now' 등 처리
        if any(x in time_str for x in ['방금', 'just now', 'moment']):
            return now.isoformat()

        # 절대 날짜 형식 시도 (예: "2024. 1. 20." 또는 "2024. 1. 20. 오전 10:30")
        try:
            # 숫자와 마침표만 추출 (날짜 부분만 가져오기 위해)
            clean_date = re.sub(r'[^0-9.]', ' ', time_str).strip()
            # 연속된 공백 제거 및 마침표 주변 공백 정리
            clean_date = re.sub(r'\s+', ' ', clean_date)
            parts = [p for p in clean_date.split() if '.' in p or len(p) == 4] # 연도가 포함된 부분 찾기
            
            # 마침표로 구분된 숫자들 추출
            date_match = re.findall(r'(\d{4})[\.\s-]+(\d{1,2})[\.\s-]+(\d{1,2})', time_str)
            if date_match:
                year, month, day = map(int, date_match[0])
                return datetime(year, month, day).isoformat()
        except:
            pass

        # 숫자 추출 (상대 시간용)
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
        time.sleep(3) # 초기 로딩 대기 (5s -> 3s)

        collected_data = []
        seen_ids = set() # 중복 방지를 위한 셋
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        video_id = url.split("/post/")[-1].split("?")[0]

        while len(collected_data) < limit:
            # 기존 구조(renderer)와 새로운 구조(view-model) 모두 대응
            comment_threads = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer, ytd-comment-view-model")
            
            for thread in comment_threads:
                if len(collected_data) >= limit:
                    break
                
                try:
                    # 데이터 추출 시도 (구조별 대응)
                    try:
                        author_elem = thread.find_element(By.CSS_SELECTOR, "#author-text, #name")
                        author = author_elem.text.strip()
                        content = thread.find_element(By.CSS_SELECTOR, "#content-text").text.strip()
                        likes_text = thread.find_element(By.CSS_SELECTOR, "#vote-count-middle, #vote-count-separator + span").text.strip()
                    except Exception as e:
                        # logger.debug(f"Basic element match failed: {e}")
                        continue

                    likes = self._parse_likes(likes_text)

                    # 고유 ID 및 링크 추출
                    comment_id = None
                    try:
                        # 기존 로직과 동일하게 lc= 뒤의 전체 문자열을 ID로 사용 (중복 방지 핵심)
                        link_elements = thread.find_elements(By.CSS_SELECTOR, "a[href*='lc=']")
                        if link_elements:
                            comment_id = link_elements[0].get_attribute("href").split("lc=")[-1]
                    except:
                        pass
                        
                    if not comment_id:
                        hash_input = f"{author}_{content[:50]}".encode('utf-8')
                        comment_id = f"hash_{hashlib.md5(hash_input).hexdigest()}"

                    # 날짜 텍스트 추출 (다양한 선택자 시도)
                    time_text = ""
                    # 1. lc= 파라미터가 있는 날짜 링크 우선 시도
                    try:
                        date_links = thread.find_elements(By.CSS_SELECTOR, "a[href*='lc=']")
                        for link in date_links:
                            # 텍스트가 있고 작성자 이름과 다르며 날짜 관련 패턴이 있는 경우
                            t = link.text.strip()
                            if t and t != author and any(x in t for x in ['전', 'ago', '.']):
                                time_text = link.get_attribute("aria-label") or t
                                if time_text: break
                    except:
                        pass

                    if not time_text:
                        # 2. 기존 방식 및 백업 선택자들
                        date_selectors = [
                            ".published-time-text a", 
                            "#header-author a.yt-simple-endpoint",
                            "#header-author a:not(#author-text)",
                            ".published-time-text"
                        ]
                        
                        for selector in date_selectors:
                            try:
                                elem = thread.find_element(By.CSS_SELECTOR, selector)
                                t = elem.text.strip()
                                # 작성자 이름과 겹치는 경우 건너뜀
                                if t == author: continue
                                
                                time_text = elem.get_attribute("aria-label") or t
                                if time_text: break
                            except:
                                continue
                    
                    if not time_text:
                        logger.warning(f"Failed to extract time for comment by {author}. Defaulting to now.")

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
            time.sleep(1.5) # 데이터 로딩 대기 (3s -> 1.5s)
            
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                time.sleep(1) # 마지막 확인 (2s -> 1s)
                if self.driver.execute_script("return document.documentElement.scrollHeight") == last_height:
                    break
            last_height = new_height

        logger.info(f"Total unique collected: {len(collected_data)} community comments.")
        return collected_data

    def close(self):
        self.driver.quit()
