import logging
from database.supabase_client import SupabaseManager
from analyzer.sentiment_analyzer import SentimentAnalyzer
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_local_analysis():
    db = SupabaseManager()
    sentiment = SentimentAnalyzer()
    
    logger.info("=== [Stage 3] 로컬 감성 분석(BERT) 시작 ===")
    
    while True:
        try:
            # 로컬 분석(sentiment_label)이 완료되지 않은 데이터 가져오기
            response = db.client.table("im_sung_gen_youtube_comments")\
                .select("comment_id, content, video_id")\
                .is_("sentiment_label", "null")\
                .limit(100)\
                .execute()
            
            rows = response.data
            if not rows:
                logger.info("✅ 모든 데이터의 로컬 분석이 완료되었습니다.")
                break

            updated_data = []
            for row in tqdm(rows, desc="BERT Analyzing"):
                label, score = sentiment.analyze(row["content"])
                updated_data.append({
                    "comment_id": row["comment_id"],
                    "video_id": row["video_id"],
                    "content": row["content"], # 데이터 무결성을 위해 content 포함
                    "sentiment_label": label,
                    "sentiment_score": score
                })

            if updated_data:
                db.upsert_comments(updated_data)
                logger.info(f"Successfully analyzed {len(updated_data)} comments.")
                
        except Exception as e:
            logger.error(f"Error during local analysis: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_local_analysis()
