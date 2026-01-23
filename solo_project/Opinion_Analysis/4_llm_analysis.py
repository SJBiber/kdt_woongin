import logging
from database.supabase_client import SupabaseManager
from analyzer.deepseek_analyzer import DeepSeekAnalyzer
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_llm_analysis():
    db = SupabaseManager()
    llm = DeepSeekAnalyzer()
    
    batch_size = 20
    logger.info(f"=== [Stage 4] LLM 정밀 분석(DeepSeek) 시작 (배치: {batch_size}) ===")
    
    while True:
        try:
            # LLM 분석(llm_sentiment)이 완료되지 않은 데이터 가져오기
            response = db.client.table("im_sung_gen_youtube_comments")\
                .select("comment_id, content, published_at, video_id")\
                .is_("llm_sentiment", "null")\
                .order("published_at")\
                .limit(batch_size)\
                .execute()
            
            rows = response.data
            if not rows:
                logger.info("✅ 모든 데이터의 LLM 정밀 분석이 완료되었습니다.")
                break

            texts = [r["content"] for r in rows]
            dates = [str(r["published_at"])[:10] for r in rows]

            # DeepSeek 호출 (날짜 맥락 포함)
            llm_results = llm.analyze_batch(texts, dates)
            logger.info(f"{llm_results}")
            updated_data = []
            for i, row in enumerate(rows):
                val = None
                if i < len(llm_results):
                    try:
                        val = int(llm_results[i])
                    except: val = None
                
                # 결과가 유효할 때만 업데이트 리스트에 추가
                if val is not None and 0 <= val <= 5:
                    updated_data.append({
                        "comment_id": row["comment_id"],
                        "video_id": row["video_id"], # 필수 컬럼 추가
                        "llm_sentiment": val
                    })

            if updated_data:
                db.upsert_comments(updated_data)
                logger.info(f"Successfully updated {len(updated_data)} comments with LLM results.")
            else:
                logger.warning("No valid LLM results returned in this batch.")
                # 분석 실패 시 무한 루프 방지를 위해 아주 잠시 대기
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_llm_analysis()
