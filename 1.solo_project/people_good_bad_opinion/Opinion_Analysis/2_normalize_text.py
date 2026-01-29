import logging
from database.supabase_client import SupabaseManager
from analyzer.nlp_engine import NLPEngine
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_normalization():
    db = SupabaseManager()
    # 맞춤법 교정 비활성화 (속도 최적화: 3-5배 향상)
    nlp = NLPEngine(use_corrector=False)
    
    logger.info("=== [Stage 2] 텍스트 정규화 및 키워드 추출 시작 ===")
    logger.info("⚡ 맞춤법 교정 비활성화 - 고속 처리 모드")
    
    total_processed = 0
    total_time = 0
    
    while True:
        try:
            # 텍스트 정제(keywords)가 완료되지 않은 데이터 가져오기 (video_id 포함)
            response = db.client.table("im_sung_gen_youtube_comments")\
                .select("comment_id, content, video_id")\
                .is_("keywords", "null")\
                .limit(50)\
                .execute()
            
            rows = response.data
            if not rows:
                logger.info("✅ 모든 데이터의 정규화가 완료되었습니다.")
                if total_processed > 0:
                    avg_time = total_time / total_processed
                    logger.info(f"📊 총 처리: {total_processed}개, 평균 처리 시간: {avg_time:.2f}초/배치")
                break

            batch_start = time.time()
            
            # 배치 단위로 맞춤법 교정 및 특수문자 제거 (성능 최적화)
            contents = [row["content"] for row in rows]
            clean_texts = nlp.preprocess_batch(contents)
            
            # 키워드 추출 (개별 처리 필요)
            updated_data = []
            for row, clean_text in tqdm(
                zip(rows, clean_texts), 
                total=len(rows),
                desc="Extracting keywords"
            ):
                keywords = nlp.extract_keywords(clean_text)
                
                updated_data.append({
                    "comment_id": row["comment_id"],
                    "video_id": row["video_id"],
                    "content": row["content"], # 데이터 무결성을 위해 content 포함
                    "keywords": keywords
                })

            if updated_data:
                db.upsert_comments(updated_data)
                
                batch_time = time.time() - batch_start
                total_time += batch_time
                total_processed += 1
                
                logger.info(f"✅ {len(updated_data)}개 댓글 정규화 완료 (소요 시간: {batch_time:.2f}초)")
                
        except Exception as e:
            logger.error(f"Error during normalization: {e}")
            time.sleep(5) # 에러 시 잠시 대기

if __name__ == "__main__":
    run_normalization()

