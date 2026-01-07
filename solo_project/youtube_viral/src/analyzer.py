from datetime import datetime, timezone
import numpy as np

class ViralAnalyzer:
    def analyze_keyword_snapshot(self, search_results: list, stats_list: list):
        """
        [고도화] 단일 시점의 데이터를 분석하여 트렌드 파워를 도출합니다.
        1. 시간당 조회수 (Power Score)
        2. 최근 업로드 비중 (Upload Density)
        3. 평균 조회수 (Average Views)
        """
        if not stats_list: return {"power_score": 0, "recent_ratio": 0, "avg_views": 0, "total_vols": 0}
        
        now = datetime.now(timezone.utc)
        total_power = 0
        total_views = 0
        recent_count = 0
        
        for stat in stats_list:
            total_views += stat["view_count"]
            
            # 1. Power Score 계산
            pub_at = datetime.fromisoformat(stat["published_at"].replace("Z", "+00:00"))
            hours_passed = max(0.5, (now - pub_at).total_seconds() / 3600)
            velocity = stat["view_count"] / hours_passed
            total_power += velocity
            
            # 2. 최근 업로드 여부 (24시간 이내)
            if hours_passed <= 24:
                recent_count += 1
                
        avg_power = total_power / len(stats_list)
        avg_views = total_views / len(stats_list)
        recent_ratio = recent_count / len(stats_list)
        
        return {
            "power_score": avg_power,
            "recent_ratio": recent_ratio,
            "avg_views": avg_views,
            "total_vols": len(search_results)
        }

    def calculate_topic_share(self, keyword: str, trending_videos: list):
        """인기 급상승 영상 중 해당 키워드가 차지하는 비중(%)을 계산합니다."""
        if not trending_videos: return 0.0
        match_count = sum(1 for v in trending_videos if keyword in v['snippet']['title'])
        return (match_count / len(trending_videos)) * 100
