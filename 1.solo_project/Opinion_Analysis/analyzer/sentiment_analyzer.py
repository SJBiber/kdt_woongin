import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_name="Jinuuuu/KoELECTRA_fine_tunning_emotion"):
        """
        감성 분석 모델 초기화
        기본 모델: Jinuuuu/KoELECTRA_fine_tunning_emotion (6~7개 감정 분류 가능)
        """
        try:
            logger.info(f"Loading emotion model: {model_name}")
            self.classifier = pipeline("sentiment-analysis", model=model_name)
            logger.info("Emotion model loaded successfully.")
            
            # 모델의 라벨을 표준 라벨로 맵핑하는 사전 (정수형)
            self.label_map = {
                'happy': 0,        # support
                'surprise': 0,     # support
                'angry': 1,        # anger
                'anxious': 2,      # neutral
                'embarrassed': 2,  # neutral
                'sad': 3,          # disappointment
                'heartache': 3     # disappointment
            }
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            self.classifier = None

    def analyze(self, text):
        """
        텍스트 감성 분석 (6종 정수 라벨 반환)
        :return: (label_int, score)
        """
        if not self.classifier or not text:
            return 2, 0.0 # 중립(neutral)
            
        try:
            # 텍스트 길이 제한
            result = self.classifier(text[:500])[0]
            raw_label = result['label']
            score = result['score']
            
            # 표준 정수 라벨로 변환
            standard_label = self.label_map.get(raw_label, 2)
            return standard_label, score
        except Exception as e:
            logger.error(f"Error during emotion analysis: {e}")
            return 2, 0.0 # 에러 시 중립 처리

if __name__ == "__main__":
    # 간단 테스트
    logging.basicConfig(level=logging.INFO)
    analyzer = SentimentAnalyzer()
    samples = [
        "진짜 너무 맛있어요 감동입니다",
        "다시는 안 갈 것 같아요. 실망입니다.",
        "그냥 그래요 보통이에요"
    ]
    for s in samples:
        label, score = analyzer.analyze(s)
        print(f"Text: {s} -> {label} ({score:.4f})")
