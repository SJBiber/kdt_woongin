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
        print("\n" + "="*80)
        print("📊 특정 업로드 날짜의 시계열 데이터 확인")
        print("="*80 + "\n")
        
        db = TrendDatabase()
        
        # 예시: 1월 19일에 업로드된 영상들의 추이
        keyword = "임성근 쉐프"
        upload_date = date(2026, 1, 19)
        
        data = db.get_upload_date_timeline(keyword, upload_date)
        
        if not data:
            print(f"❌ {upload_date}에 업로드된 영상 데이터가 없습니다.")
            return
        
        print(f"📅 업로드 날짜: {upload_date}")
        print(f"📹 키워드: {keyword}")
        print(f"📊 총 {len(data)}번 수집됨\n")
        
        print("-" * 80)
        print(f"{'수집일':<12} {'조회수':>12} {'댓글':>8} {'좋아요':>8} {'조회증가':>12} {'댓글증가':>8} {'좋아증가':>8}")
        print("-" * 80)
        
        for row in data:
            collected = row['collected_date']
            views = row['total_views']
            comments = row['total_comments']
            likes = row['total_likes']
            v_growth = row.get('views_growth', 0)
            c_growth = row.get('comments_growth', 0)
            l_growth = row.get('likes_growth', 0)
            
            print(f"{collected:<12} {views:>12,} {comments:>8,} {likes:>8,} "
                  f"{v_growth:>+12,} {c_growth:>+8,} {l_growth:>+8,}")
        
        print("-" * 80)
        print("\n💡 이렇게 매일 같은 업로드 날짜의 영상들을 재조회하여")
        print("   관심도 변화를 추적할 수 있습니다!\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
