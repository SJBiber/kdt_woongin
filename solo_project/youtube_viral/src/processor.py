import re
from collections import Counter

class TrendProcessor:
    def __init__(self):
        # 제외할 일반적인 단어 (순수 기능어로 제한)
        self.common_stopwords = {
            '쇼츠', 'shorts', 'short', '영상', '오늘', '정말', '진짜', '너무', '최고', 
            '공개', '최신', '추천', '인기', '급상승', '티비', 'TV', '에피소드'
        }

    def extract_keywords(self, videos: list, top_n=10):
        """
        [고도화] 모든 분야(카테고리)의 키워드를 고르게 분석하기 위해 
        카테고리별 분산 추출(Stratified Extraction) 방식을 사용합니다.
        """
        from collections import defaultdict
        
        # 1. 카테고리별로 영상 그룹핑 및 단어 분석
        category_word_groups = defaultdict(list)
        for v in videos:
            cat_id = v['snippet'].get('categoryId', '0')
            text = v['snippet']['title'] + " " + " ".join(v['snippet'].get('tags', []))
            cleaned = re.sub(r'[^\w\s]', ' ', text)
            tokens = [t for t in cleaned.split() if len(t) > 1 and t not in self.common_stopwords]
            category_word_groups[cat_id].extend(tokens)

        # 2. 각 카테고리별 상위 키워드 산출
        cat_top_keywords = {}
        for cat_id, words in category_word_groups.items():
            counts = Counter(words)
            cat_top_keywords[cat_id] = [w for w, c in counts.most_common(5)]

        # 3. 전 분야에서 고르게 키워드 선발 (Round-Robin 방식)
        unique_selected = []
        rank_idx = 0
        
        while len(unique_selected) < top_n and rank_idx < 5:
            # 모든 카테고리를 순회하며 1위, 2위... 순으로 하나씩 선발
            for cat_id in sorted(cat_top_keywords.keys()):
                if rank_idx < len(cat_top_keywords[cat_id]):
                    word = cat_top_keywords[cat_id][rank_idx]
                    if word not in unique_selected:
                        unique_selected.append(word)
                if len(unique_selected) >= top_n: break
            rank_idx += 1

        return unique_selected
