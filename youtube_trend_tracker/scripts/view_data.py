"""
수집된 데이터 조회 스크립트
Supabase에 저장된 트렌드 데이터를 확인
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
import pandas as pd

# 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """데이터 조회"""
    try:
        print("\n" + "="*80)
        print("📊 YouTube 트렌드 데이터 조회")
        print("="*80 + "\n")
        
        db = TrendDatabase()
        
        # 최신 데이터 조회
        keyword = "임성근 쉐프"
        data = db.get_latest_trends(keyword, limit=100)
        
        if not data:
            print("❌ 데이터가 없습니다.")
            return
        
        # DataFrame으로 변환
        df = pd.DataFrame(data)
        
        # 날짜별로 정렬
        df = df.sort_values('upload_date', ascending=False)
        
        print(f"✅ 총 {len(df)}개 레코드 조회\n")
        
        # 요약 통계
        print("📈 업로드 날짜별 통계:")
        print("-" * 80)
        
        for _, row in df.iterrows():
            upload_date = row['upload_date']
            collected_date = row['collected_date']
            video_count = row['video_count']
            total_views = row['total_views']
            views_growth = row.get('views_growth', 0)
            views_growth_rate = row.get('views_growth_rate', 0)
            
            if views_growth == 0:
                status = "🆕 첫 수집"
            elif views_growth_rate > 10:
                status = f"📈 +{views_growth:,} (+{views_growth_rate:.1f}%)"
            elif views_growth_rate > 0:
                status = f"➡️ +{views_growth:,} (+{views_growth_rate:.1f}%)"
            else:
                status = f"📉 {views_growth:,} ({views_growth_rate:.1f}%)"
            
            print(f"📅 {upload_date} (수집: {collected_date})")
            print(f"   영상: {video_count}개 | 조회수: {total_views:,} | {status}")
            print()
        
        # 전체 통계
        print("="*80)
        print("📊 전체 통계:")
        print(f"   총 영상 수: {df['video_count'].sum():,}개")
        print(f"   총 조회수: {df['total_views'].sum():,}")
        print(f"   평균 조회수/영상: {df['total_views'].sum() / df['video_count'].sum():,.0f}")
        print(f"   최고 조회수 날짜: {df.loc[df['total_views'].idxmax(), 'upload_date']}")
        print(f"   최다 영상 날짜: {df.loc[df['video_count'].idxmax(), 'upload_date']}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
