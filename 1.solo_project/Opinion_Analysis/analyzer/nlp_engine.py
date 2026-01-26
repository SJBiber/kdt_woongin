from soynlp.tokenizer import LTokenizer
import re
import logging
from .corrector import TyposCorrector

logger = logging.getLogger(__name__)

class NLPEngine:
    def __init__(self, use_corrector=True):
        # soynlp는 학습 기반이므로 간단한 키워드 추출을 위해 LTokenizer 사용
        self.tokenizer = LTokenizer()
        self.corrector = TyposCorrector() if use_corrector else None
        logger.info(f"NLPEngine initialized (use_corrector={use_corrector}).")

        # 포괄적 불용어 리스트 (유튜브 댓글 분석 최적화)
        self.stopwords = set([
            # 조사
            '의','가','이','은','들','는','을','를','으로','로','에','에게','에서','부터','까지','만','도','나','이나','라도','마저','조차','과','와','하고','랑','이랑',
            
            # 어미 및 접미사
            '고','지','며','거나','든지','던','었','았','겠','네요','어요','아요','해요','해','요','서','니','다','ㅂ니다','습니다',
            
            # 대명사 및 지시어
            '저','나','너','우리','저희','여기','거기','저기','이것','그것','저것','뭐','누구','어디','언제','왜','어떻게','무엇','자','한',
            
            # 감탄사 및 추임새 (유튜브 특화)
            'ㅋㅋ','ㅋㅋㅋ','ㅎㅎ','ㅠㅠ','ㅜㅜ','ㄷㄷ','ㄹㅇ','ㅇㅈ','ㅇㅋ','ㅋ','ㄱ','ㅂ','ㅅ','ㅈ','ㅊ','ㅍ','ㅎ',
            '하','히','호','후','헉','엥','어','음','흠','아이고','어머','세상에','와','우와','오오','오','아','에','이','와우','허걱','헐','앗','응','네',
            
            # 빈도 높은 동사/형용사
            '있다','없다','되다','하다','이다','아니다','같다','보다','주다','받다','하는','되는','있는','없는','같은','보는','이런','저런','그런','내',
            
            # 유튜브 댓글 특화
            '임성근','임짱','임','성근','장군','사단장','군인','군대','부대','해병대','해병',
            '영상','댓글','유튜브','구독','좋아요','알림','설정','채널','보고','봤','봄','보니',
            
            # 부사 및 접속사
            '진짜','너무','정말','진짜로','매우','완전','엄청','되게','좀','약간','조금','많이','더','덜','제일','가장','잘','걍',
            '그냥','그','해서','그래','그래도','그거','이거','저거','뭔가','대박',
            '그리고','그러나','하지만','그래서','따라서','또','또한','역시','물론',
            
            # 시간 및 수량 표현
            '오늘','어제','내일','지금','요즘','최근','예전','전','후','때','중','개','명','번','차','년','월','일','시','분'
        ])

    def preprocess(self, text):
        """텍스트 정제 및 맞춤법 교정 (단일)"""
        if not text:
            return ""
        
        # 1. 맞춤법 및 오타 교정 (먼저 수행하여 문맥 보존)
        if self.corrector:
            text = self.corrector.correct(text)
            
        # 2. 특수문자 제거
        clean_text = re.sub(r'[^가-힣0-9\s]', '', text)
        return clean_text

    def preprocess_batch(self, texts):
        """텍스트 정제 및 맞춤법 교정 (배치) - 성능 최적화"""
        if not texts:
            return []
        
        # 1. 맞춤법 및 오타 교정 (배치 처리)
        if self.corrector:
            corrected_texts = self.corrector.correct_batch(texts)
        else:
            corrected_texts = texts
            
        # 2. 특수문자 제거
        clean_texts = [re.sub(r'[^가-힣0-9\s]', '', text) for text in corrected_texts]
        return clean_texts

    def extract_keywords(self, text, min_length=2):
        """단어 추출 (LTokenizer 기반)"""
        if not text:
            return []
        
        try:
            # 텍스트에서 토큰 추출
            tokens = self.tokenizer.tokenize(text)
            # 불용어 제거 및 길이 제한
            keywords = [word for word in tokens if word not in self.stopwords and len(word) >= min_length]
            return list(set(keywords)) # 중복 제거
        except Exception as e:
            logger.error(f"Error during keyword extraction: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = NLPEngine()
    sample = "흑백요리사 너무 재밌어요! 출연자분들 요리 실력이 정말 대단하네요. 특히 인성이 좋은 것 같아요."
    clean = engine.preprocess(sample)
    keywords = engine.extract_keywords(clean)
    print(f"Original: {sample}")
    print(f"Keywords: {keywords}")

