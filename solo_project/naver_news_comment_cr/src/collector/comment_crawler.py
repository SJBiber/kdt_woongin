"""
네이버 뉴스 댓글 크롤링 모듈
Selenium을 사용한 동적 크롤링
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from config.settings import MAX_COMMENTS_PER_NEWS


class NaverCommentCrawler:
    """네이버 뉴스 댓글 크롤러"""
    
    def __init__(self, headless: bool = True):
        """
        초기화
        
        Args:
            headless: 헤드리스 모드 사용 여부
        """
        self.headless = headless
        self.driver = None
        print("✅ 댓글 크롤러 초기화")
    
    def _init_driver(self):
        """Chrome 드라이버 초기화"""
        if self.driver:
            return
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome 드라이버 시작")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✅ Chrome 드라이버 종료")
    
    def extract_news_id(self, url: str) -> Optional[str]:
        """
        뉴스 URL에서 기사 ID 추출
        
        Args:
            url: 네이버 뉴스 URL
            
        Returns:
            기사 ID (oid_aid 형식)
        """
        try:
            # URL 파라미터에서 oid와 aid 추출
            # 예: https://n.news.naver.com/article/001/0014123456
            # 또는 https://news.naver.com/main/read.naver?oid=001&aid=0014123456
            
            if '/article/' in url:
                # 새 형식
                parts = url.split('/article/')[-1].split('/')
                if len(parts) >= 2:
                    oid, aid = parts[0], parts[1].split('?')[0]
                    return f"{oid}_{aid}"
            elif 'oid=' in url and 'aid=' in url:
                # 구 형식
                params = url.split('?')[-1].split('&')
                oid = aid = None
                for param in params:
                    if param.startswith('oid='):
                        oid = param.split('=')[1]
                    elif param.startswith('aid='):
                        aid = param.split('=')[1]
                if oid and aid:
                    return f"{oid}_{aid}"
            
            # 추출 실패시 URL 해시 사용
            return hashlib.md5(url.encode()).hexdigest()[:16]
            
        except Exception as e:
            print(f"❌ 뉴스 ID 추출 실패: {e}")
            return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def crawl_comments(self, news_url: str, max_comments: int = MAX_COMMENTS_PER_NEWS) -> List[Dict]:
        """
        특정 뉴스의 댓글 크롤링
        
        Args:
            news_url: 네이버 뉴스 URL
            max_comments: 최대 수집 댓글 수
            
        Returns:
            댓글 데이터 리스트
        """
        self._init_driver()
        
        news_id = self.extract_news_id(news_url)
        print(f"📰 뉴스 ID: {news_id}")
        
        try:
            # 페이지 로드
            self.driver.get(news_url)
            time.sleep(2)
            
            # 댓글 영역으로 스크롤
            try:
                comment_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "cbox_module"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", comment_section)
                time.sleep(1)
            except TimeoutException:
                print("⚠️  댓글 영역을 찾을 수 없음 (댓글이 없는 기사일 수 있음)")
                return []
            
            # iframe으로 전환 (네이버 댓글은 iframe 내부에 있음)
            try:
                iframe = self.driver.find_element(By.ID, "cbox_module")
                self.driver.switch_to.frame(iframe)
                time.sleep(1)
            except NoSuchElementException:
                print("⚠️  댓글 iframe을 찾을 수 없음")
                return []
            
            comments = []
            
            # 댓글 더보기 버튼 클릭 (최대 댓글 수까지)
            while len(comments) < max_comments:
                try:
                    # 더보기 버튼 찾기
                    more_button = self.driver.find_element(By.CLASS_NAME, "u_cbox_btn_more")
                    if more_button.is_displayed():
                        more_button.click()
                        time.sleep(0.5)
                    else:
                        break
                except NoSuchElementException:
                    break
                except Exception as e:
                    print(f"⚠️  더보기 버튼 클릭 중 오류: {e}")
                    break
            
            # 댓글 요소 수집
            comment_elements = self.driver.find_elements(By.CLASS_NAME, "u_cbox_comment")
            
            for idx, elem in enumerate(comment_elements[:max_comments], 1):
                try:
                    comment_data = self._parse_comment_element(elem, news_id, idx)
                    if comment_data:
                        comments.append(comment_data)
                except Exception as e:
                    print(f"⚠️  댓글 파싱 실패 (idx={idx}): {e}")
                    continue
            
            # iframe에서 나오기
            self.driver.switch_to.default_content()
            
            print(f"✅ {len(comments)}개 댓글 수집 완료")
            return comments
            
        except Exception as e:
            print(f"❌ 댓글 크롤링 실패: {e}")
            return []
    
    def _parse_comment_element(self, element, news_id: str, idx: int) -> Optional[Dict]:
        """
        댓글 요소에서 데이터 추출
        
        Args:
            element: Selenium 웹 요소
            news_id: 뉴스 ID
            idx: 댓글 인덱스
            
        Returns:
            댓글 데이터 딕셔너리
        """
        try:
            # 작성자
            author_elem = element.find_element(By.CLASS_NAME, "u_cbox_nick")
            author = author_elem.text.strip()
            
            # 댓글 내용
            content_elem = element.find_element(By.CLASS_NAME, "u_cbox_contents")
            content = content_elem.text.strip()
            
            if not content:
                return None
            
            # 공감/비공감 수
            try:
                like_elem = element.find_element(By.CLASS_NAME, "u_cbox_cnt_recomm")
                likes = int(like_elem.text.strip() or 0)
            except:
                likes = 0
            
            try:
                dislike_elem = element.find_element(By.CLASS_NAME, "u_cbox_cnt_unrecomm")
                dislikes = int(dislike_elem.text.strip() or 0)
            except:
                dislikes = 0
            
            # 작성 시간
            try:
                time_elem = element.find_element(By.CLASS_NAME, "u_cbox_date")
                time_text = time_elem.text.strip()
                published_at = self._parse_datetime(time_text)
            except:
                published_at = datetime.now().isoformat()
            
            # 댓글 고유 ID 생성 (뉴스ID + 작성자 + 내용 해시)
            comment_id = hashlib.md5(
                f"{news_id}_{author}_{content}_{idx}".encode()
            ).hexdigest()
            
            return {
                'comment_id': comment_id,
                'news_id': news_id,
                'author': author,
                'content': content,
                'likes': likes,
                'dislikes': dislikes,
                'published_at': published_at,
                'sentiment_label': None,
                'sentiment_score': None,
                'llm_sentiment': None,
                'keywords': None
            }
            
        except Exception as e:
            print(f"❌ 댓글 요소 파싱 실패: {e}")
            return None
    
    @staticmethod
    def _parse_datetime(time_text: str) -> str:
        """
        네이버 댓글 시간 텍스트를 ISO 형식으로 변환
        
        Args:
            time_text: "2시간 전", "2024.01.23. 오후 2:30" 등
            
        Returns:
            ISO 형식 날짜 문자열
        """
        try:
            # 간단한 처리: 현재 시간 반환 (추후 정밀한 파싱 추가 가능)
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()


if __name__ == "__main__":
    # 테스트
    crawler = NaverCommentCrawler(headless=False)
    
    # 테스트용 뉴스 URL (실제 URL로 교체 필요)
    test_url = "https://n.news.naver.com/article/001/0014123456"
    
    comments = crawler.crawl_comments(test_url, max_comments=10)
    
    for i, comment in enumerate(comments, 1):
        print(f"\n{i}. {comment['author']}: {comment['content'][:50]}...")
        print(f"   공감: {comment['likes']}, 비공감: {comment['dislikes']}")
    
    crawler.close()
