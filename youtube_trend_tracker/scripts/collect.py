"""
YouTube 트렌드 통합 수집 스크립트
- API 키 자동 전환 기능
- 날짜 범위 지정 수집
- 에러 처리 및 재시도
"""
import sys
import io
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tracker_advanced import AdvancedTrendTracker
from datetime import date, timedelta

# 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """통합 수집 실행"""
    try:
        print("\n" + "="*60)
        print("📥 YouTube 트렌드 통합 수집 시스템")
        print("="*60 + "\n")
        
        tracker = AdvancedTrendTracker()
        
        # 설정
        keyword = "임성근 쉐프"
        
        # 수집 범위 설정
        print("📌 수집 범위를 선택하세요:")
        print("   1. 전체 기간 (2025-09-01 ~ 어제)")
        print("   2. 특정 기간 지정")
        print("   3. 최근 N일")
        
        choice = input("\n선택 (1/2/3): ").strip()
        
        if choice == "1":
            # 전체 기간
            start_date = date(2025, 9, 1)
            end_date = date.today() - timedelta(days=1)
        elif choice == "2":
            # 특정 기간
            start_str = input("시작 날짜 (YYYY-MM-DD): ").strip()
            end_str = input("종료 날짜 (YYYY-MM-DD): ").strip()
            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str)
        elif choice == "3":
            # 최근 N일
            days = int(input("최근 며칠? ").strip())
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=days-1)
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        total_days = (end_date - start_date).days + 1
        
        print(f"\n📌 수집 설정:")
        print(f"   - 키워드: {keyword}")
        print(f"   - 수집 범위: {start_date} ~ {end_date}")
        print(f"   - 총 기간: {total_days}일")
        print(f"   - API 예상 소모량: 약 {total_days * 100} 유닛")
        print(f"   - 예상 소요 시간: 약 {total_days * 2} 분\n")
        
        response = input("⚠️  계속 진행하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("❌ 취소되었습니다.")
            return
        
        print("\n🚀 수집 시작...\n")
        print("💡 Tip: API 할당량 초과 시 자동으로 다음 키로 전환됩니다.\n")
        
        # 트렌드 추적 실행
        tracker.track_date_range(keyword, start_date, end_date)
        
        print("\n" + "="*60)
        print("✅ 수집 완료!")
        print("="*60)
        print("\n📊 다음 단계:")
        print("   1. python3 view_data.py 로 데이터 확인")
        print("   2. Streamlit 대시보드 구현")
        print("   3. 트렌드 분석\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 수집 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
