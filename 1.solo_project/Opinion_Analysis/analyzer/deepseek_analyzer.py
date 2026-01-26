import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.error("DeepSeek API Key is missing. Please set it in .env file.")
            self.client = None
        else:
            # DeepSeek는 OpenAI 호환 API를 사용합니다.
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            logger.info("DeepSeek Analyzer initialized.")

    def analyze_batch(self, texts, dates=None):
        """
        여러 개의 댓글을 날짜 정보와 함께 6가지 감정 카테고리로 상세 분석
        """
        if not self.client or not texts:
            return []

        # 날짜 정보가 있으면 댓글 옆에 표시, 없으면 텍스트만 나열
        if dates and len(dates) == len(texts):
            flat_texts = "\n".join([f"{i+1}. [{dates[i]}] {texts[i]}" for i, t in enumerate(texts)])
        else:
            flat_texts = "\n".join([f"{i+1}. {t}" for i, t in enumerate(texts)])
        
        prompt = f"""
        유튜버에 대한 댓글 감성 분류 (총 {len(texts)}개). 
        각 댓글 앞의 [YYYY-MM-DD] 날짜를 참고하여 반드시 아래 6가지 카테고리에 맞는 숫자로만 분류하세요:

        [카테고리 항목]
        0: support (고마움(비꼬는것이 아닌 순수한 고마움), 도움된다, 사랑, 지지, 응원, 복귀 기대("언제와요", "보고싶다"), 사과 수용, 위로, "정치인보다 이분이다" 식의 방어/옹호)
        1: anger (분노, 욕설, 공격적 비판, 나락, 전과자 언급 등 강한 적대감)
        2: neutral (중립, 감정 없는 짧은 인사, 무의미한 나열, 주제를 벗어난 과도한 정치 댓글)
        3: disappointment (실망, 유감, "믿었는데 아쉽다", 팬이었으나 돌아섬, 구독취소 언급)
        4: sarcasm (조롱, 비꼼, 반어법, 밈(Meme) 사용, 비꼬는 의도의 이모티콘('^^', 'ㅋㅋ' 등 문맥상 조롱 , 칭찬하는척하면서 비꼬는글))
        5: inquiry (질문, 정보 요청, 상황 파악, 또는 유튜버가 아닌 '작성자들끼리 싸우는 댓글')

        [날짜 기반 시점 맥락 및 중요 지침]
        1. 기준점: 1월 19일 해당 유투버의 음주운전 전과 고백 및 사과문이 발생했습니다.
        2. [2026-01-18] 이전: 과한 칭찬이나 음식 맛에 대한 칭찬도 , 최고,  응원은 대부분 '0'(support)입니다, 
        3. [2026-01-19] 이후: 칭찬하는 척 하거나 "역시 임짱", "대단하다" 같은 표현은 무조건 '4'(sarcasm)일 가능성이 99%입니다. 날짜를 보고 비꼬는 것인지 진심인지 판단하세요.
        4. 감정 구분: 
           - 1번(anger) vs 4번(sarcasm): 1번은 직접적인 욕설/분노, 4번은 비꼬는 말투/반어법.
           - 3번(disappointment) vs 4번(sarcasm): 3번은 실망/원망의 표현, 4번은 비꼼.
           - 2번(neutral) vs 4번(sarcasm): 2번은 무의미한 나열, 4번은 뉘앙스가 담긴 비꼼.
        5. 유저 간 분쟁: 유튜버 욕이 아니라 작성자끼리 싸우는 내용은 5번(inquiry/기타)으로 분류합니다.
        6. 결과는 반드시`[0, 1, 3, 4, 2, ...]` 형식의 정수 배열로만 응답하세요.

        댓글 리스트:
        {flat_texts}
        """

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"너는 유튜버에 대한 댓글의 미묘한 뉘앙스와 날짜별 맥락 변화를 완벽히 파악하는 감정 분석 마스터야. 입력받은 {len(texts)}개의 댓글에 대해 **반드시 순서에 맞게** 개수 누락 없이 정확히 {len(texts)}개의 정수를 담은 JSON 배열만 반환해."},
                    {"role": "user", "content": prompt},
                ],
                response_format={ "type": "json_object" },
                stream=False
            )
            data = json.loads(response.choices[0].message.content)

            # JSON 내의 결과 배열 추출
            if isinstance(data, list):
                return data
            return data.get("results", data.get("sentiments", list(data.values())[0]))
        except Exception as e:
            logger.error(f"DeepSeek Batch API Error: {e}")
            return []

if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO)
    analyzer = DeepSeekAnalyzer()
    test_texts = ["와 진짜 대단하시네요 역시 임짱 ㅋㅋ", "언제와요? 기다릴게요!"]
    test_dates = ["2026-01-20", "2026-01-15"]
    res = analyzer.analyze_batch(test_texts, test_dates)
    print(f"Analysis Results: {res}")
