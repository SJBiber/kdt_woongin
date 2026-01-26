"""
특정 업로드 날짜의 시계열 데이터 확인
"""
import sys
import io
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import TrendDatabase
from datetime import date

# 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """시계열 데이터 조회"""
    try:
        print("\n" + "="*100)
        print("📊 수집 기간별 전체 영상 통계 비교 (증감률 추이)")
        print("="*100 + "\n")
        
        db = TrendDatabase()
        
        keyword = "임성근 쉐프"
        
        # 수집 날짜별로 그룹화된 데이터 조회
        response = db.supabase.table("daily_video_trends").select("*").eq(
            "keyword", keyword
        ).order(
            "collected_date", desc=False
        ).execute()
        
        if not response.data:
            print(f"❌ '{keyword}' 데이터가 없습니다.")
            return
        
        # 수집 날짜별로 합계 계산
        from collections import defaultdict
        collected_stats = defaultdict(lambda: {
            'total_views': 0,
            'total_comments': 0,
            'total_likes': 0,
            'video_count': 0
        })
        
        for row in response.data:
            collected_date = row['collected_date']
            collected_stats[collected_date]['total_views'] += row['total_views']
            collected_stats[collected_date]['total_comments'] += row['total_comments']
            collected_stats[collected_date]['total_likes'] += row['total_likes']
            collected_stats[collected_date]['video_count'] += row['video_count']
        
        # 날짜순으로 정렬
        sorted_dates = sorted(collected_stats.keys())
        
        print(f"📹 키워드: {keyword}")
        print(f"📊 총 {len(sorted_dates)}번 수집됨\n")
        
        print("-" * 100)
        print(f"{'수집일':<12} {'조회수':>12} {'댓글':>8} {'좋아요':>8} {'조회증가':>12} {'댓글증가':>8} {'좋아증가':>8} {'증감률':>12}")
        print("-" * 100)
        
        prev_views = None
        prev_comments = None
        prev_likes = None
        
        for collected_date in sorted_dates:
            stats = collected_stats[collected_date]
            views = stats['total_views']
            comments = stats['total_comments']
            likes = stats['total_likes']
            
            # 증감량 계산
            if prev_views is not None:
                v_growth = views - prev_views
                c_growth = comments - prev_comments
                l_growth = likes - prev_likes
                
                # 증감률 계산 (%)
                v_rate = (v_growth / prev_views * 100) if prev_views > 0 else 0
                
                print(f"{collected_date:<12} {views:>12,} {comments:>8,} {likes:>8,} "
                      f"{v_growth:>+12,} {c_growth:>+8,} {l_growth:>+8,} {v_rate:>+11.2f}%")
            else:
                print(f"{collected_date:<12} {views:>12,} {comments:>8,} {likes:>8,} "
                      f"{'(기준)':>12} {'(기준)':>8} {'(기준)':>8} {'(기준)':>12}")
            
            # 다음 반복을 위해 저장
            prev_views = views
            prev_comments = comments
            prev_likes = likes
        
        print("-" * 100)
        print("\n💡 수집 날짜별로 전체 영상들의 합계를 비교하여")
        print("   전체적인 관심도 변화 추이를 확인할 수 있습니다!")
        print("   증감률은 조회수 기준으로 계산됩니다.\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
