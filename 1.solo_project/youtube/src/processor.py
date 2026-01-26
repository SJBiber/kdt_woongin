import re

class KeywordProcessor:
    def __init__(self):
        self.stopwords = {'shorts', '쇼츠', '영상', '오늘', '유튜브', '추천', '인기'}

    def process_video_keywords(self, video):
        """영상 제목과 태그에서 핵심 키워드를 추출합니다."""
        title = video['snippet']['title']
        tags = video['snippet'].get('tags', [])
        
        # 텍스트 결합 후 특수문자 제거
        combined_text = title + " " + " ".join(tags)
        cleaned_text = re.sub(r'[^\w\s]', ' ', combined_text)
        
        # 토큰화 및 필터링
        tokens = cleaned_text.split()
        keywords = [t for t in tokens if len(t) > 1 and t.lower() not in self.stopwords]
        
        # 중복 제거 후 상위 5개 유지
        unique_keywords = list(dict.fromkeys(keywords))
        return ", ".join(unique_keywords[:5])
