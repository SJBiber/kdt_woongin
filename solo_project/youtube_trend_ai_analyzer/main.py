from src.database import TrendDatabase
from src.ai_engine import GeminiAnalyzer
from datetime import datetime
import json

def run_ai_category_analysis():
    print(f"--- [{datetime.now()}] AI Category Aggregation Started ---")
    
    db = TrendDatabase()
    ai = GeminiAnalyzer()

    for atype in ["TRENDING", "HISTORICAL"]:
        try:
            print(f"\nProcessing {atype} data...")
            # 1. 최신 데이터 로드
            df = db.fetch_latest_video_keywords(analysis_type=atype, limit=20)
            
            if df.empty:
                print(f"No {atype} data found. Skipping...")
                continue

            # 2. AI 분석 및 카테고리 집계 (대표 키워드 + 조회수 합계)
            print(f"Aggregating {atype} by AI categories...")
            category_results = ai.analyze_and_aggregate_categories(df, atype)

            # 3. DB 저장
            if category_results:
                print(f"Saving {len(category_results)} categories to Supabase...")
                db.save_category_trends(category_results)
                
                # 결과 출력
                for res in category_results:
                    print(f"  - [{res['category_name']}] 영상: {res['video_count']}개, 총 조회수: {res['total_views']:,}")
            
        except Exception as e:
            print(f"Error occurred during {atype} analysis: {e}")

    print("\n--- AI Category Analysis Completed ---")

if __name__ == "__main__":
    run_ai_category_analysis()
