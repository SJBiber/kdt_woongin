from google import genai
import json
import re
from configs.settings import settings

class GeminiAnalyzer:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
            
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = 'gemini-flash-latest'

    def analyze_and_aggregate_categories(self, df, analysis_type):
        """데이터를 분석하여 카테고리별로 집계된 JSON 데이터를 반환합니다."""
        if df.empty: return []

        # AI에게 전달할 데이터 포맷 (제목, 조회수, 키워드)
        data_list = []
        for _, row in df.iterrows():
            data_list.append({
                "title": row['title'],
                "view_count": int(row['view_count']),
                "keywords": row['keywords']
            })

        prompt = f"""
        당신은 유투브 데이터 분석가입니다. 
        제공된 유투브 영상 리스트를 분석하여, 각 영상을 가장 적절한 '대표 카테고리'로 분류하고 카테고리별 총 합계를 계산해주세요.

        [분석할 데이터 ({analysis_type})]
        {json.dumps(data_list, ensure_ascii=False, indent=2)}

        [요구사항]
        1. 각 영상을 하나의 대표 카테고리(예: 게임, 영화, 음악, 사회/뉴스, 라이프스타일, 스포츠 등)로 분류하세요.
        2. 동일한 카테고리에 속한 영상들의 개수(video_count)와 조회수 합계(total_views)를 계산하세요.
        3. 각 카테고리를 잘 나타내는 대표 키워드들을 3개 정도 선정하세요.
        4. 반드시 아래 JSON 형식으로만 응답하세요. 다른 설명은 생략하세요.

        [JSON 응답 형식]
        [
            {{
                "category_name": "카테고리명",
                "video_count": 0,
                "total_views": 0,
                "representative_keywords": "키워드1, 키워드2, 키워드3",
                "analysis_type": "{analysis_type}"
            }}
        ]
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        return self._parse_json_response(response.text)

    def _parse_json_response(self, text):
        """AI 응답에서 JSON 데이터만 추출해 파싱합니다."""
        try:
            # 마크다운 블록 제거
            clean_text = re.sub(r'```json\n?|```', '', text).strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"JSON 파싱 에러: {e}\n원본 텍스트: {text}")
            return []
