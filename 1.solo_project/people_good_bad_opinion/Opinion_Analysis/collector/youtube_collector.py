import logging
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
from datetime import datetime
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        self.downloader = YoutubeCommentDownloader()

    def _parse_likes(self, likes_text):
        if likes_text is None:
            return 0
        if isinstance(likes_text, int):
            return likes_text
            
        likes_text = str(likes_text).strip().replace(",", "")
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

    def fetch_comments(self, video_url, limit=None):
        logger.info(f"Fetching comments from: {video_url}")
        comments = self.downloader.get_comments_from_url(video_url, sort_by=SORT_BY_RECENT)
        
        collected_data = []
        seen_ids = set()
        count = 0
        
        for comment in comments:
            if limit and count >= limit:
                break
                
            try:
                if "v=" in video_url:
                    video_id = video_url.split("v=")[1].split("&")[0]
                elif "/shorts/" in video_url:
                    video_id = video_url.split("/shorts/")[1].split("?")[0]
                else:
                    video_id = video_url.split("/")[-1].split("?")[0]
                
                cid = comment.get("cid")
                # 중복 데이터 체크
                if cid in seen_ids:
                    continue
                    
                data = {
                    "comment_id": cid,
                    "video_id": video_id,
                    "author": comment.get("author"),
                    "content": comment.get("text"),
                    "likes": self._parse_likes(comment.get("votes", 0)),
                    "published_at": self._format_date(comment),
                }
                collected_data.append(data)
                seen_ids.add(cid)
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"Collected {count} comments...")
                    
            except Exception as e:
                logger.error(f"Error parsing comment: {e}")
                continue
                
        logger.info(f"Total unique collected: {len(collected_data)} comments.")
        return collected_data

    def _format_date(self, comment):
        """'time_parsed' 필드를 우선 사용하고, 없을 경우 'time' 텍스트를 파싱하여 ISO 날짜로 변환"""
        time_parsed = comment.get("time_parsed")
        if time_parsed:
            try:
                # time_parsed가 float(유닉스 타임스탬프)인 경우 처리
                return datetime.fromtimestamp(time_parsed).isoformat()
            except Exception as e:
                logger.debug(f"Error converting time_parsed: {e}")

        time_str = comment.get("time", "")
        if not time_str:
            return datetime.now().isoformat()
            
        from datetime import timedelta
        
        now = datetime.now()
        
        # '방금', 'just now' 등 처리
        if any(x in time_str for x in ['방금', 'just now', 'moment']):
            return now.isoformat()

        # 절대 날짜 형식 시도 (예: "2024. 1. 20.")
        try:
            date_match = re.findall(r'(\d{4})[\.\s-]+(\d{1,2})[\.\s-]+(\d{1,2})', time_str)
            if date_match:
                year, month, day = map(int, date_match[0])
                return datetime(year, month, day).isoformat()
        except:
            pass

        # 숫자 추출
        match = re.search(r'(\d+)', time_str)
        if not match:
            return now.isoformat()
            
        value = int(match.group(1))
        
        # 단위별 역산 (한국어/영어 모두 대응)
        # '시간'이 '일' 보다 먼저 체크되도록 하여 '1시간 전'이 '1일 전'으로 오인되지 않게 함
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
