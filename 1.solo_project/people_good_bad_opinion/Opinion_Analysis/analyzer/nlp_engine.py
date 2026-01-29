"""
NLP 엔진 모듈 (nlp_engine.py)
==============================
한국어 텍스트 전처리 및 키워드 추출을 담당하는 핵심 NLP 모듈.

주요 기능:
    1. 텍스트 전처리: 오타 교정(T5 기반) + 특수문자 제거
    2. 키워드 추출 : Kiwi 형태소 분석 → 품사 필터링 → 불용어 제거 → 중복 제거
    3. 사용자 사전  : 복합어/고유명사가 분리되지 않도록 Kiwi 사전에 사전 등록

사용 예시:
    >>> engine = NLPEngine(use_corrector=False)
    >>> clean = engine.preprocess("음주운전은 절대 안 됩니다!")
    >>> keywords = engine.extract_keywords(clean)
    >>> print(keywords)  # ['음주운전'] — "음주" + "운전" 분리 없이 추출

의존성:
    - kiwipiepy : 한국어 형태소 분석기 (세종 태그셋 기반)
    - corrector : T5 기반 오타 교정 모듈 (analyzer/corrector.py)
"""

from kiwipiepy import Kiwi
import re
import logging
from .corrector import TyposCorrector

logger = logging.getLogger(__name__)


class NLPEngine:
    """
    한국어 NLP 처리 엔진.

    파이프라인:
        원본 텍스트
          → [preprocess] 오타 교정 + 특수문자 제거
          → [extract_keywords] Kiwi 형태소 분석 → 명사/형용사 추출 → 불용어 제거

    Attributes:
        KEYWORD_POS_TAGS (set): 키워드로 추출할 품사 태그 집합
        USER_DICT (list): Kiwi 사용자 사전에 등록할 (단어, 품사태그) 튜플 리스트
        tokenizer (Kiwi): Kiwi 형태소 분석기 인스턴스
        corrector (TyposCorrector | None): T5 기반 오타 교정기 (비활성화 가능)
        stopwords (set): 키워드 추출 시 제외할 불용어 집합
    """

    # ──────────────────────────────────────────────
    # 클래스 상수
    # ──────────────────────────────────────────────

    # 키워드로 추출할 품사 태그 (세종 태그셋 기준)
    # NNG: 일반명사 (예: 운전, 요리)
    # NNP: 고유명사 (예: 이재명, 흑백요리사)
    # VA : 형용사   (예: 좋다, 대단하다)
    KEYWORD_POS_TAGS = {'NNG', 'NNP', 'VA'}

    # Kiwi 사용자 사전: 분리되면 의미가 달라지는 복합어/고유명사 등록
    # ※ 새 단어를 추가하려면 여기에 ('단어', '품사태그') 튜플을 추가하면 됨
    # 품사 태그 참고:
    #   NNG = 일반명사 (합성어, 복합어 등)
    #   NNP = 고유명사 (인명, 프로그램명, 브랜드명 등)
    USER_DICT = [
        ('음주운전', 'NNG'),    # "음주" + "운전" 분리 방지 → 하나의 일반명사로 처리
        ('이재명', 'NNP'),      # "이재" + "명" 분리 방지 → 인명 고유명사로 처리
        ('이재명 대통령', 'NNP'),      # "이재" + "명" 분리 방지 → 인명 고유명사로 처리
        ('흑백요리사', 'NNP'),  # "흑백" + "요리사" 분리 방지 → 프로그램명 고유명사로 처리
    ]

    # ──────────────────────────────────────────────
    # 초기화
    # ──────────────────────────────────────────────

    def __init__(self, use_corrector=True):
        """
        NLP 엔진 초기화.

        Args:
            use_corrector (bool): True이면 T5 기반 오타 교정기를 활성화.
                                  False이면 교정 없이 특수문자 제거만 수행.
                                  (교정기 비활성화 시 3~5배 속도 향상)
        """
        # ① Kiwi 형태소 분석기 초기화
        self.tokenizer = Kiwi()

        # ② 사용자 사전 등록 — 복합어/고유명사가 분리되지 않도록 예외 처리
        #    add_user_word(word, tag)는 Kiwi 내부 사전에 단어를 추가하여
        #    형태소 분석 시 해당 단어를 하나의 토큰으로 인식하게 함
        for word, tag in self.USER_DICT:
            self.tokenizer.add_user_word(word, tag)
        logger.info(f"Kiwi 사용자 사전 등록 완료: {[w for w, _ in self.USER_DICT]}")

        # ③ 오타 교정기 초기화 (선택적)
        self.corrector = TyposCorrector() if use_corrector else None
        logger.info(f"NLPEngine initialized with Kiwi (use_corrector={use_corrector}).")

        # ④ 불용어 사전 정의
        # - 조사/어미/부사 등 기능어는 Kiwi POS 필터링(KEYWORD_POS_TAGS)으로 자동 제거됨
        # - 여기서는 POS 필터를 통과하지만 분석 가치가 없는 "의미적 불용어"만 관리
        self.stopwords = set([
            # === 범용 명사 (지시어·단위어 등, 분석 가치 없음) ===
            '것', '거', '게', '걸', '건', '겁',  # 의존명사 (것의 구어체 변형)
            '수', '때', '중', '등',                # 의존명사
            '년', '월', '일', '번', '개', '명',    # 단위 명사
            '차', '전', '후', '데', '점', '쪽',    # 위치/시간 명사

            # === 초빈출 동사/형용사 (Kiwi lemma 사전형) ===
            # Kiwi는 활용형을 lemma(사전형)로 변환하므로 '~다' 형태로 등록
            '있다', '없다', '되다', '하다', '이다', '아니다', '같다',
            '보다', '주다', '받다', '싶다', '알다', '모르다',
            '오다', '가다', '나오다', '들다', '보이다', '만들다',

            # === 유튜브/플랫폼 메타 명사 ===
            # 댓글 수집 플랫폼 특성상 빈출하지만 여론 분석에 무의미한 단어
            '영상', '댓글', '유튜브', '구독', '좋아요', '알림', '채널',
            '클릭', '링크', '공유', '저장', '재생', '시청', '조회',
            '추천', '답글', '대댓글',

            # === 프로젝트 특화 고유명사 ===
            # 분석 대상 인물명 자체는 모든 댓글에 등장하므로 키워드에서 제외
            '임성근', '백종원',

            # === 범용 의미 필러 ===
            # 문맥 없이 단독으로는 의미 파악이 어려운 추상 명사
            '사람', '말', '생각', '정도', '부분', '경우', '느낌',
        ])

    # ──────────────────────────────────────────────
    # 텍스트 전처리
    # ──────────────────────────────────────────────

    def preprocess(self, text):
        """
        단일 텍스트 전처리 (오타 교정 + 특수문자 제거).

        처리 순서:
            1. T5 기반 오타 교정 (corrector 활성화 시)
               — 특수문자 제거 전에 수행하여 문맥 정보를 최대한 보존
            2. 정규식으로 한글·숫자·공백 외 모든 문자 제거

        Args:
            text (str): 원본 텍스트 (예: YouTube 댓글)

        Returns:
            str: 정제된 텍스트. 빈 입력이면 빈 문자열 반환.
        """
        if not text:
            return ""

        # 1단계: 맞춤법 및 오타 교정 (문맥 보존을 위해 특수문자 제거 전에 수행)
        if self.corrector:
            text = self.corrector.correct(text)

        # 2단계: 특수문자 제거 — 한글(가-힣), 숫자(0-9), 공백만 남김
        # 이모지, 영문, 특수기호 등이 제거됨
        clean_text = re.sub(r'[^가-힣0-9\s]', '', text)
        return clean_text

    def preprocess_batch(self, texts):
        """
        배치 텍스트 전처리 — 대량 처리 시 성능 최적화.

        preprocess()와 동일한 로직이지만, corrector의 배치 처리(GPU 병렬화)를
        활용하여 대량 텍스트 처리 속도를 개선함.

        Args:
            texts (list[str]): 원본 텍스트 리스트

        Returns:
            list[str]: 정제된 텍스트 리스트. 빈 입력이면 빈 리스트 반환.
        """
        if not texts:
            return []

        # 1단계: 맞춤법 및 오타 교정 (배치 처리 — GPU 가속 활용)
        if self.corrector:
            corrected_texts = self.corrector.correct_batch(texts)
        else:
            corrected_texts = texts

        # 2단계: 특수문자 제거 (리스트 컴프리헨션으로 일괄 처리)
        clean_texts = [re.sub(r'[^가-힣0-9\s]', '', text) for text in corrected_texts]
        return clean_texts

    # ──────────────────────────────────────────────
    # 키워드 추출
    # ──────────────────────────────────────────────

    def extract_keywords(self, text, min_length=2):
        """
        Kiwi 형태소 분석 기반 키워드 추출.

        처리 순서:
            1. Kiwi 형태소 분석 (tokenize) — 텍스트를 형태소 단위로 분리
            2. 품사(POS) 필터링 — NNG(일반명사), NNP(고유명사), VA(형용사)만 선택
            3. lemma(사전형) 추출 — 활용형을 사전형으로 통일 (예: "재밌어요" → "재밌다")
            4. 불용어 제거 — self.stopwords에 등록된 무의미 단어 제외
            5. 최소 길이 필터 — 1글자 키워드 제외 (기본값 2자 이상)
            6. 중복 제거 — set()으로 동일 키워드 병합

        Args:
            text (str): 전처리된 텍스트 (preprocess() 결과)
            min_length (int): 최소 키워드 길이 (기본값 2, 1글자 단어 제외)

        Returns:
            list[str]: 추출된 키워드 리스트 (중복 제거됨). 에러 시 빈 리스트.

        Examples:
            >>> engine.extract_keywords("음주운전은 절대 안 됩니다")
            ['음주운전']  # "음주" + "운전" 분리 없이 하나의 키워드로 추출
        """
        if not text:
            return []

        try:
            # Kiwi 형태소 분석 — 각 토큰은 (form, tag, start, end, score, lemma) 정보를 가짐
            tokens = self.tokenizer.tokenize(text)

            # 4단계 필터링: 품사 → 불용어 → 최소 길이
            keywords = [
                token.lemma                              # lemma: 사전형 (활용형 → 원형)
                for token in tokens
                if token.tag in self.KEYWORD_POS_TAGS    # ① 품사 필터 (명사/형용사만)
                and token.lemma not in self.stopwords    # ② 불용어 제거
                and len(token.lemma) >= min_length       # ③ 최소 길이 필터
            ]
            return list(set(keywords))  # ④ 중복 제거
        except Exception as e:
            logger.error(f"Error during keyword extraction: {e}")
            return []


# ──────────────────────────────────────────────────
# 테스트 실행 (직접 실행 시)
# ──────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = NLPEngine(use_corrector=False)

    # 사용자 사전 등록이 제대로 동작하는지 검증하는 테스트 케이스
    # 기대: "흑백요리사", "음주운전", "이재명"이 분리되지 않고 하나의 키워드로 추출됨
    test_cases = [
        "흑백요리사 너무 재밌어요! 출연자분들 요리 실력이 정말 대단하네요.",
        "음주운전은 절대 하면 안 됩니다.",
        "이재명 대통령 관련 뉴스가 많다.",
    ]
    for sample in test_cases:
        clean = engine.preprocess(sample)
        keywords = engine.extract_keywords(clean)
        print(f"Original: {sample}")
        print(f"Cleaned:  {clean}")
        print(f"Keywords: {keywords}")
        print()
