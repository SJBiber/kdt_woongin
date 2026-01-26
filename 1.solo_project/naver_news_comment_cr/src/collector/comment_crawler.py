"""
네이버 뉴스 댓글 수집 모듈
네이버 뉴스 댓글 API(cbox)를 직접 호출하여 수집
"""

import requests
import json
import time
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from config.settings import MAX_COMMENTS_PER_NEWS


class NaverCommentCrawler:
    """네이버 뉴스 댓글 크롤러 (API 기반)"""
    
    def __init__(self, headless: bool = True):
        """초기화"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://news.naver.com/',
            'Accept': '*/*',
        }
        print("✅ 댓글 크롤러 초기화 (API 방식)")
    
    def close(self):
        """종료 처리"""
        pass
    
    def extract_news_info(self, url: str) -> Dict[str, str]:
        """URL에서 oid, aid 및 섹션 추출"""
        try:
            oid = ""
            aid = ""
            if '/article/' in url:
                parts = url.split('/article/')[-1].split('/')
                if len(parts) >= 2:
                    oid, aid = parts[0], parts[1].split('?')[0]
            elif 'oid=' in url and 'aid=' in url:
                params = url.split('?')[-1].split('&')
                for param in params:
                    if param.startswith('oid='):
                        oid = param.split('=')[1]
                    elif param.startswith('aid='):
                        aid = param.split('=')[1]
            
            return {
                "oid": oid, 
                "aid": aid,
                "news_id": f"{oid}_{aid}" if oid and aid else hashlib.md5(url.encode()).hexdigest()[:16]
            }
        except Exception:
            return {"oid": "", "aid": "", "news_id": hashlib.md5(url.encode()).hexdigest()[:16]}

    def _get_api_response(self, oid: str, aid: str, template_id: str, page: int):
        """실제 API 호출 및 파싱"""
        # 가장 범용적인 cbox API 엔드포인트
        api_url = "https://apis.naver.com/commentBox/cbox/web/commentList.json"
        params = {
            'ticket': 'news',
            'templateId': template_id,
            'pool': 'cbox5',
            'lang': 'ko',
            'country': 'KR',
            'objectId': f'news{oid},{aid}', 
            'pageSize': 20,
            'page': page,
            'sort': 'favorite',
            'initialize': 'true' if page == 1 else 'false',
            'useIntermReactions': 'true',
            'listType': 'OBJECT'
        }
        
        try:
            response = requests.get(api_url, params=params, headers=self.headers)
            if response.status_code != 200:
                return None
            
            res_text = response.text
            if "(" in res_text:
                res_text = res_text[res_text.find("(")+1:res_text.rfind(")")]
            return json.loads(res_text)
        except:
            return None

    def crawl_comments(self, news_url: str, max_comments: int = MAX_COMMENTS_PER_NEWS) -> List[Dict]:
        """네이버 뉴스 댓글 API를 호출하여 데이터 수집"""
        info = self.extract_news_info(news_url)
        oid, aid, news_id = info["oid"], info["aid"], info["news_id"]
        
        if not oid or not aid:
            return []

        print(f"📰 뉴스 ID: {news_id} (수집 중...)")
        
        all_comments = []
        page = 1
        
        # 시도해볼 templateId 목록
        # 네이버는 섹션에 따라 템플릿 ID가 다를 수 있으나, 보통 view_news가 범용적입니다.
        template_ids = ["view_news", "view_economy", "view_society", "view_politics"]
        
        # 적절한 templateId 찾기
        current_template = template_ids[0]
        
        try:
            while len(all_comments) < max_comments:
                data = self._get_api_response(oid, aid, current_template, page)
                
                # 실패 시 templateId 바꿔서 재시도
                if not data or not data.get('success'):
                    success = False
                    for tid in template_ids[1:]:
                        data = self._get_api_response(oid, aid, tid, page)
                        if data and data.get('success'):
                            current_template = tid
                            success = True
                            break
                    if not success:
                        print("⚠️  댓글 API를 호출할 수 없거나 댓글이 비활성화되었습니다.")
                        break
                
                result = data.get('result', {})
                comment_list = result.get('commentList', [])
                
                if not comment_list:
                    break
                
                for item in comment_list:
                    if len(all_comments) >= max_comments:
                        break
                    if item.get('status') != 'ON':
                        continue
                        
                    all_comments.append({
                        'comment_id': str(item.get('commentNo')),
                        'news_id': news_id,
                        'author': item.get('userName', '비공개'),
                        'content': item.get('contents', ''),
                        'likes': item.get('sympathyCount', 0),
                        'dislikes': item.get('antipathyCount', 0),
                        'published_at': item.get('modTime', item.get('regTime', datetime.now().isoformat())),
                        'sentiment_label': None,
                        'sentiment_score': None,
                        'llm_sentiment': None,
                        'keywords': None
                    })
                
                page_info = result.get('pageModel', {})
                if page >= page_info.get('totalPages', 0):
                    break
                page += 1
                time.sleep(0.1)

            print(f"✅ {len(all_comments)}개 댓글 수집 완료")
            return all_comments

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return []


if __name__ == "__main__":
    crawler = NaverCommentCrawler()
    test_url = "https://n.news.naver.com/mnews/article/243/0000091781?sid=101"
    comments = crawler.crawl_comments(test_url, max_comments=10)
    for c in comments:
        print(f"[{c['author']}] {c['content'][:30]}...")
