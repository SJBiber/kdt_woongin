import sys
import os
from pathlib import Path

# 현재 파일(main.py)의 위치를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from src.collector import YouTubeCollector
from src.processor import TrendProcessor
from src.analyzer import ViralAnalyzer
from src.notifier import Notifier
from src.visualizer import TrendVisualizer
from configs.settings import settings
import asyncio
from datetime import datetime
from src.database import DatabaseManager

async def run_viral_radar():
    print(f"--- [{datetime.now()}] Viral Radar Snapshot Workflow Started ---")
    
    collector = YouTubeCollector()
    processor = TrendProcessor()
    analyzer = ViralAnalyzer()
    notifier = Notifier()
    db = DatabaseManager()

    try:
        # 1. 인기 급상승 영상 수집 (300개 - 6 units 소모)
        trending_videos = collector.get_trending_videos(max_results=300)
        
        # 1-1. 인기 급상승 소스 스냅샷 보관 (v2.5 추가)
        snapshots = []
        for i, v in enumerate(trending_videos):
            snapshots.append({
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "channel_title": v["snippet"]["channelTitle"],
                "rank": i + 1,
                "view_count": int(v["statistics"].get("viewCount", 0)),
                "like_count": int(v["statistics"].get("likeCount", 0))
            })
        db.save_trending_snapshots(snapshots)
        print(f"Saved {len(snapshots)} trending snapshots for source analysis.")

        # 2. 키워드 추출 (상위 8개 집중)
        top_keywords = processor.extract_keywords(trending_videos, top_n=settings.TOP_KEYWORDS_COUNT)
        print(f"Analyzing Optimized Top {len(top_keywords)} Keywords: {top_keywords}")

        all_analysis_results = []
        for kw in top_keywords:
            # 주요 분석 수행...
            share = analyzer.calculate_topic_share(kw, trending_videos)
            search_results = collector.search_by_keyword(kw, max_results=settings.SEARCH_MAX_RESULTS)
            video_ids = [v["id"]["videoId"] for v in search_results]
            stats_list = collector.get_video_stats(video_ids)
            
            results = analyzer.analyze_keyword_snapshot(search_results, stats_list)
            
            # 결과 객체 생성
            analysis_item = {
                "keyword": kw,
                "topic_share": share,
                "power_score": results["power_score"],
                "recent_ratio": results["recent_ratio"],
                "avg_views": results["avg_views"],
                "total_vols": results["total_vols"]
            }
            all_analysis_results.append(analysis_item)

            print(f"[{kw}] Share: {share:.1f}% | Power: {results['power_score']:.0f} | Recent: {results['recent_ratio']*100:.1f}% | AvgViews: {results['avg_views']:.0f}")

            # DB 기록 및 알림 (v2.5 신규 스냅샷 테이블 대응)
            db.save_trend_analysis([analysis_item])
            
            # 알림 조건 판별 및 전송...
            if results["recent_ratio"] > settings.SURGE_THRESHOLD_RATIO:
                msg = f"키워드 '{kw}'의 신규 업로드 비중이 {results['recent_ratio']*100:.1f}%로 매우 높습니다!"
                await notifier.send_alert("Trend Surge Detected", msg, 
                    {"Keyword": kw, "Topic Share": f"{share:.1f}%", "Power Score": f"{results['power_score']:.0f}"})
                db.save_viral_alert({"keyword": kw, "alert_type": "SURGE", "score_value": results["recent_ratio"], "description": msg})

            if results["power_score"] > settings.VIRAL_THRESHOLD_POWER:
                msg = f"키워드 '{kw}' 관련 영상들이 시간당 평균 {results['power_score']:.0f}회의 조회를 기록 중입니다!"
                await notifier.send_alert("High Power Trend", msg, 
                    {"Keyword": kw, "Power Score": f"{results['power_score']:.0f}", "Recent Ratio": f"{results['recent_ratio']*100:.1f}%"})
                db.save_viral_alert({"keyword": kw, "alert_type": "POWER", "score_value": results["power_score"], "description": msg})

        # 5. [v2.5] 대시보드 리포트 생성
        visualizer = TrendVisualizer()
        visualizer.generate(all_analysis_results)

    except Exception as e:
        import traceback
        print(f"Error in Workflow: {e}")
        traceback.print_exc()

    print("--- Viral Radar Workflow Completed ---")

def job():
    asyncio.run(run_viral_radar())

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # 즉시 실행
    job()
    # 주기 설정 (인기 급상승 확인)
    scheduler.add_job(job, 'interval', minutes=settings.TREND_CHECK_INTERVAL)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Stopped.")
