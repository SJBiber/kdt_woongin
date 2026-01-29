import logging
from database.supabase_client import SupabaseManager
from analyzer.deepseek_analyzer import DeepSeekAnalyzer
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 논란 기준 날짜 (음주운전 전과 고백일)
CONTROVERSY_DATE = "2026-01-19"

def process_batch(db, llm, rows, analyze_func):
    """배치 데이터를 분석하고 DB에 업데이트하는 공통 로직"""
    texts = [r["content"] for r in rows]
    dates = [str(r["published_at"])[:10] for r in rows]

    # DeepSeek 호출
    llm_results = analyze_func(texts, dates)
    logger.info(f"LLM Results: {llm_results}")

    updated_data = []
    for i, row in enumerate(rows):
        val = None
        if i < len(llm_results):
            try:
                val = int(llm_results[i])
            except:
                val = None

        # 결과가 유효할 때만 업데이트 리스트에 추가
        if val is not None and 0 <= val <= 5:
            updated_data.append({
                "comment_id": row["comment_id"],
                "video_id": row["video_id"],
                "content": row["content"],
                "llm_sentiment": val
            })

    if updated_data:
        db.upsert_comments(updated_data)
        logger.info(f"Successfully updated {len(updated_data)} comments with LLM results.")
        return True
    else:
        logger.warning("No valid LLM results returned in this batch.")
        return False

def run_llm_analysis_before_controversy(db, llm, batch_size):
    """논란 전 댓글 분석 (2026-01-18 이전)"""
    logger.info(f"=== 논란 전 댓글 분석 시작 ({CONTROVERSY_DATE} 이전) ===")

    while True:
        try:
            # 논란 전 데이터 가져오기 (llm_sentiment가 null이고, 날짜가 논란일 이전)
            response = db.client.table("im_sung_gen_youtube_comments")\
                .select("comment_id, content, published_at, video_id")\
                .is_("llm_sentiment", "null")\
                .lt("published_at", CONTROVERSY_DATE)\
                .order("published_at")\
                .limit(batch_size)\
                .execute()

            rows = response.data
            if not rows:
                logger.info("✅ 논란 전 댓글 분석 완료.")
                break

            logger.info(f"논란 전 댓글 {len(rows)}개 분석 중...")
            success = process_batch(db, llm, rows, llm.analyze_batch_before_controversy)

            if not success:
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error during pre-controversy analysis: {e}")
            time.sleep(5)

def run_llm_analysis_after_controversy(db, llm, batch_size):
    """논란 후 댓글 분석 (2026-01-19 이후)"""
    logger.info(f"=== 논란 후 댓글 분석 시작 ({CONTROVERSY_DATE} 이후) ===")

    while True:
        try:
            # 논란 후 데이터 가져오기 (llm_sentiment가 null이고, 날짜가 논란일 이후)
            response = db.client.table("im_sung_gen_youtube_comments")\
                .select("comment_id, content, published_at, video_id")\
                .is_("llm_sentiment", "null")\
                .gte("published_at", CONTROVERSY_DATE)\
                .order("published_at")\
                .limit(batch_size)\
                .execute()

            rows = response.data
            if not rows:
                logger.info("✅ 논란 후 댓글 분석 완료.")
                break

            logger.info(f"논란 후 댓글 {len(rows)}개 분석 중...")
            success = process_batch(db, llm, rows, llm.analyze_batch_after_controversy)

            if not success:
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error during post-controversy analysis: {e}")
            time.sleep(5)

def run_llm_analysis():
    """메인 분석 함수 - 논란 전/후 각각 처리"""
    db = SupabaseManager()
    llm = DeepSeekAnalyzer()

    batch_size = 20
    logger.info(f"=== [Stage 4] LLM 정밀 분석(DeepSeek) 시작 (배치: {batch_size}) ===")
    logger.info(f"논란 기준일: {CONTROVERSY_DATE}")

    # 1. 논란 전 댓글 분석
    run_llm_analysis_before_controversy(db, llm, batch_size)

    # 2. 논란 후 댓글 분석
    run_llm_analysis_after_controversy(db, llm, batch_size)

    logger.info("=== 모든 LLM 분석 완료 ===")

if __name__ == "__main__":
    run_llm_analysis()
