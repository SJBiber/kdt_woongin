import logging
from database.supabase_client import SupabaseManager
from analyzer.deepseek_baek_jongwon_analyzer import DeepSeekBaekJongwonAnalyzer
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_llm_analysis():
    db = SupabaseManager()
    llm = DeepSeekBaekJongwonAnalyzer()
    
    batch_size = 20
    logger.info(f"=== [백종원 Stage 4] LLM 정밀 분석(DeepSeek) 시작 (배치: {batch_size}) ===")
    logger.info("📌 임성근과 동일한 6가지 카테고리 (0-5) 사용")
    logger.info("   0:support, 1:anger, 2:neutral, 3:disappointment, 4:sarcasm, 5:inquiry")
    
    while True:
        try:
            # LLM 분석(llm_sentiment)이 완료되지 않은 데이터 가져오기
            response = db.client.table("baek_jongwon_youtube_comments")\
                .select("comment_id, content, published_at, video_id")\
                .is_("llm_sentiment", "null")\
                .order("published_at")\
                .limit(batch_size)\
                .execute()
            
            rows = response.data
            if not rows:
                logger.info("✅ 모든 백종원 데이터의 LLM 정밀 분석이 완료되었습니다.")
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
                
                # 결과가 유효할 때만 업데이트 리스트에 추가 (0-5 범위)
                if val is not None and 0 <= val <= 5:
                    updated_data.append({
                        "comment_id": row["comment_id"],
                        "video_id": row["video_id"],
                        "content": row["content"], # 필수 컬럼 추가
                        "llm_sentiment": val
                    })

            if updated_data:
                db.upsert_baek_jongwon_comments(updated_data)
                logger.info(f"Successfully updated {len(updated_data)} comments with LLM results.")
            else:
                logger.warning("No valid LLM results returned in this batch.")
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_llm_analysis()
