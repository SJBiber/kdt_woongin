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

    def analyze_batch_before_controversy(self, texts, dates=None):
        """
        논란 전(2026-01-18 이전) 댓글을 6가지 감정 카테고리로 분석
        - 대부분 지지, 중립, 호감형 조롱이 많음
        """
        if not self.client or not texts:
            return []

        if dates and len(dates) == len(texts):
            flat_texts = "\n".join([f"{i+1}. [{dates[i]}] {texts[i]}" for i, t in enumerate(texts)])
        else:
            flat_texts = "\n".join([f"{i+1}. {t}" for i, t in enumerate(texts)])

        prompt = f"""
        유튜버에 대한 댓글 감성 분류 (총 {len(texts)}개).
        이 댓글들은 **논란 발생 전**의 댓글들입니다. 반드시 아래 6가지 카테고리에 맞는 숫자로만 분류하세요:

        [카테고리 항목]
        0: support (지지, 응원, 좋아요, 고마움, 최고, 대단하다, 사랑, 음식 맛에 대한 칭찬, 팬심 표현, "언제와요", "보고싶다" 등 호감 표현, **호감형 조롱/놀림도 포함** - 좋아하는 마음에서 하는 장난스러운 놀림, "ㅋㅋ" 등 친근한 조롱 , 다른 사람과 비교하는 댓글(파인다이닝보단 이사람,4평 쉐프보다 이사람 같은 뉘앙스 포함))
        1: anger (분노, 욕설, 공격적 비판, 정말 싫어서 남기는 악플 - 논란 전에도 소수 존재)
        2: neutral (중립, 감정 없는 짧은 인사, 무의미한 나열, 단순 정보 전달)
        3: disappointment (실망, 유감 표현 - 논란 전에는 거의 없음)
        4: sarcasm (진짜 싫어서 하는 비꼼/조롱만 해당 - 명확히 악의적인 의도가 보이는 조롱, 비아냥)
        5: inquiry (질문, 정보 요청, 상황 파악, 작성자들끼리 싸우는 댓글, 주제를 벗어난 정치적 발언)

        [논란 전 맥락 - 중요 지침]
        1. 이 시기 댓글들은 **대부분 긍정적**입니다. 지지(0), 중립(2)이 주를 이룹니다.
        2. "대단하다", "역시", "최고", "사랑해요" 등의 표현은 **진심 어린 칭찬**으로 '0'(support)입니다.
        3. **호감형 조롱/놀림도 '0'(support)**입니다. 좋아하는 마음에서 장난치는 댓글은 지지로 분류합니다.
           - 예: "임짱 오늘도 웃기네 ㅋㅋ", "또 먹방이야? ㅋㅋ" → 0번(support)
        4. '4'(sarcasm)는 **진짜 싫어서 하는 악의적 조롱만** 해당합니다. 논란 전에는 거의 없습니다.
        5. 진짜 싫어서 남기는 악플은 명확한 욕설이면 '1'(anger), 비꼬는 말투면 '4'(sarcasm)입니다.
        6. 결과는 반드시 `[0, 1, 3, 4, 2, ...]` 형식의 정수 배열로만 응답하세요.

        댓글 리스트:
        {flat_texts}
        """

        return self._call_api(texts, prompt)

    def analyze_batch_after_controversy(self, texts, dates=None):
        """
        논란 후(2026-01-19 이후) 댓글을 6가지 감정 카테고리로 상세 분석
        - 비꼬는 댓글, 분노, 실망 등 부정적 댓글이 많음
        """
        if not self.client or not texts:
            return []

        if dates and len(dates) == len(texts):
            flat_texts = "\n".join([f"{i+1}. [{dates[i]}] {texts[i]}" for i, t in enumerate(texts)])
        else:
            flat_texts = "\n".join([f"{i+1}. {t}" for i, t in enumerate(texts)])

        prompt = f"""
        유튜버에 대한 댓글 감성 분류 (총 {len(texts)}개).
        이 댓글들은 **논란 발생 후(2026-01-19 음주운전 전과 고백 이후)**의 댓글들입니다.
        반드시 아래 6가지 카테고리에 맞는 숫자로만 분류하세요:

        [카테고리 항목]
        0: support (고마움(비꼬는것이 아닌 순수한 고마움), 도움된다, 사랑, 지지, 응원, 복귀 기대("언제와요", "보고싶다"), 사과 수용, 위로, "정치인보다 이분이다" 식의 방어/옹호)
        1: anger (분노, 욕설, 공격적 비판, 나락, 전과자 언급 등 강한 적대감)
        2: neutral (중립, 감정 없는 짧은 인사, 무의미한 나열)
        3: disappointment (실망, 유감, "믿었는데 아쉽다", 팬이었으나 돌아섬, 구독취소 언급)
        4: sarcasm (조롱, 비꼼, 반어법, 밈(Meme) 사용, 비꼬는 의도의 이모티콘('^^', 'ㅋㅋ' 등 문맥상 조롱), 칭찬하는 척하면서 비꼬는 글)
        5: inquiry (질문, 정보 요청, 상황 파악, 또는 유튜버가 아닌 '작성자들끼리 싸우는 댓글', 주제를 벗어난 과도한 정치적 발언 성향이 보이는 댓글)

        [논란 후 맥락 - 중요 지침]
        1. **핵심**: 칭찬하는 척 하거나 "역시 임짱", "대단하다" 같은 표현은 **무조건 '4'(sarcasm)일 가능성이 99%**입니다.
        2. 감정 구분:
           - 1번(anger) vs 4번(sarcasm): 1번은 직접적인 욕설/분노, 4번은 비꼬는 말투/반어법.
           - 3번(disappointment) vs 4번(sarcasm): 3번은 실망/원망의 표현, 4번은 비꼼.
           - 2번(neutral) vs 4번(sarcasm): 2번은 무의미한 나열, 4번은 뉘앙스가 담긴 비꼼.
        3. 유저 간 분쟁: 유튜버 욕이 아니라 작성자끼리 싸우는 내용은 5번(inquiry/기타)으로 분류합니다.
        4. 결과는 반드시 `[0, 1, 3, 4, 2, ...]` 형식의 정수 배열로만 응답하세요.

        댓글 리스트:
        {flat_texts}
        """

        return self._call_api(texts, prompt)

    def _call_api(self, texts, prompt):
        """DeepSeek API 호출 공통 로직"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"너는 유튜버에 대한 댓글의 미묘한 뉘앙스와 맥락을 완벽히 파악하는 감정 분석 마스터야. 입력받은 {len(texts)}개의 댓글에 대해 **반드시 순서에 맞게** 개수 누락 없이 정확히 {len(texts)}개의 정수를 담은 JSON 배열만 반환해."},
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

    def analyze_batch(self, texts, dates=None):
        """
        레거시 메서드 - 하위 호환성을 위해 유지
        논란 후 분석과 동일하게 동작
        """
        return self.analyze_batch_after_controversy(texts, dates)

if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO)
    analyzer = DeepSeekAnalyzer()
    test_texts = ["와 진짜 대단하시네요 역시 임짱 ㅋㅋ", "언제와요? 기다릴게요!"]
    test_dates = ["2026-01-20", "2026-01-15"]
    res = analyzer.analyze_batch(test_texts, test_dates)
    print(f"Analysis Results: {res}")
