from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import logging

logger = logging.getLogger(__name__)

class TyposCorrector:
    def __init__(self, model_name="j5ng/et5-typos-corrector", min_length=10):
        """
        ET5 기반 한국어 맞춤법 및 오타 교정 모델 초기화 (배치 처리 + GPU 지원)
        
        Args:
            model_name: 사용할 모델 이름
            min_length: 이 길이 미만의 텍스트는 교정 스킵 (성능 최적화)
        """
        self.min_length = min_length
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            logger.info(f"Loading Typos Corrector model: {model_name}")
            logger.info(f"Using device: {self.device}")
            
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(
                model_name, 
                use_safetensors=True
            ).to(self.device)
            
            # 평가 모드로 설정 (dropout 비활성화 등)
            self.model.eval()
            
            logger.info("Typos Corrector model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Typos Corrector: {e}")
            self.model = None

    def correct(self, text):
        """
        단일 텍스트 맞춤법 교정 수행 (하위 호환성 유지)
        """
        if not text:
            return text
        results = self.correct_batch([text])
        return results[0] if results else text

    def correct_batch(self, texts, batch_size=8):
        """
        배치 단위로 텍스트 맞춤법 교정 수행 (성능 최적화)
        
        Args:
            texts: 교정할 텍스트 리스트
            batch_size: 한 번에 처리할 배치 크기
            
        Returns:
            교정된 텍스트 리스트
        """
        if not self.model or not texts:
            return texts

        corrected_texts = []
        
        try:
            # 짧은 텍스트는 교정 스킵 (성능 향상)
            texts_to_process = []
            skip_indices = []
            
            for idx, text in enumerate(texts):
                if not text or len(text.strip()) < self.min_length:
                    skip_indices.append(idx)
                    corrected_texts.append(text)
                else:
                    texts_to_process.append((idx, text[:512]))  # 길이 제한
            
            # 배치 단위로 처리
            for i in range(0, len(texts_to_process), batch_size):
                batch = texts_to_process[i:i + batch_size]
                batch_texts = [text for _, text in batch]
                
                # 토크나이징 (패딩 적용)
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # 추론 (gradient 계산 비활성화로 메모리 절약 및 속도 향상)
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=512,
                        num_beams=3,  # 5->3으로 줄여서 속도 향상
                        early_stopping=True
                    )
                
                # 디코딩
                batch_corrected = self.tokenizer.batch_decode(
                    outputs, 
                    skip_special_tokens=True
                )
                
                # 결과 저장
                for (original_idx, _), corrected in zip(batch, batch_corrected):
                    corrected_texts.insert(original_idx, corrected)
            
            return corrected_texts
            
        except Exception as e:
            logger.error(f"Error during batch typo correction: {e}")
            return texts

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    corrector = TyposCorrector()
    
    # 단일 테스트
    test_text = "안녕하새요 반갑숨니다 마춤법이 틀려써요"
    result = corrector.correct(test_text)
    print(f"Original: {test_text}")
    print(f"Corrected: {result}")
    
    # 배치 테스트
    test_batch = [
        "안녕하새요",
        "반갑숨니다 마춤법이 틀려써요",
        "짧음",  # 스킵될 것
        "이건 정말 긴 텍스트인데 맞춤법이 많이 틀렸어요"
    ]
    results = corrector.correct_batch(test_batch)
    print("\nBatch results:")
    for orig, corr in zip(test_batch, results):
        print(f"  {orig} -> {corr}")
