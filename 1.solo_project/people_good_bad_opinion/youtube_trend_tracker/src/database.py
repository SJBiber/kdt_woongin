import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, date
import sys
import io
from pathlib import Path

# 환경 설정 로드 - config/.env 파일
config_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

# 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class TrendDatabase:
    """YouTube 트렌드 데이터 관리 클래스"""
    
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("[!] .env 파일에 Supabase 정보가 설정되어 있는지 확인해주세요.")
            
        self.supabase: Client = create_client(url, key)
        print("[✓] 데이터베이스 연결 성공")

    def save_trend_data(self, trend_data):
        """
        일별 트렌드 데이터 저장
        
        Args:
            trend_data (dict): {
                'keyword': str,
                'upload_date': date,
                'collected_date': date,
                'video_count': int,
                'total_views': int,
                'total_likes': int,
                'total_comments': int,
                'views_growth': int (optional),
                'likes_growth': int (optional),
                'comments_growth': int (optional),
                'views_growth_rate': float (optional),
                'likes_growth_rate': float (optional),
                'comments_growth_rate': float (optional)
            }
        """
        try:
            # 날짜를 문자열로 변환
            data_to_insert = trend_data.copy()
            if isinstance(data_to_insert.get('upload_date'), date):
                data_to_insert['upload_date'] = data_to_insert['upload_date'].isoformat()
            if isinstance(data_to_insert.get('collected_date'), date):
                data_to_insert['collected_date'] = data_to_insert['collected_date'].isoformat()
            
            # upsert: 같은 키가 있으면 업데이트, 없으면 삽입
            response = self.supabase.table("daily_video_trends").upsert(
                data_to_insert,
                on_conflict="keyword,upload_date,collected_date"
            ).execute()
            
            print(f"[+] 저장 완료: {trend_data['keyword']} | "
                  f"업로드: {trend_data['upload_date']} | "
                  f"수집: {trend_data['collected_date']} | "
                  f"조회수: {trend_data['total_views']:,}")
            
            return response
        except Exception as e:
            print(f"[!] 저장 중 오류: {e}")
            return None

    def get_previous_day_data(self, keyword, upload_date, collected_date):
        """
        전날 수집한 같은 업로드 날짜의 데이터 조회
        
        Args:
            keyword (str): 검색 키워드
            upload_date (date): 업로드 날짜
            collected_date (date): 현재 수집 날짜 (이 날짜의 전날 데이터를 찾음)
            
        Returns:
            dict or None: 전날 데이터
        """
        try:
            # 전날 날짜 계산
            from datetime import timedelta
            previous_date = collected_date - timedelta(days=1)
            
            response = self.supabase.table("daily_video_trends").select("*").eq(
                "keyword", keyword
            ).eq(
                "upload_date", upload_date.isoformat()
            ).eq(
                "collected_date", previous_date.isoformat()
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[!] 전날 데이터 조회 중 오류: {e}")
            return None

    def get_current_data(self, keyword, upload_date, collected_date):
        """
        현재 수집 날짜의 기존 데이터 조회 (중복 실행 시 비교용)
        
        Args:
            keyword (str): 검색 키워드
            upload_date (date): 업로드 날짜
            collected_date (date): 현재 수집 날짜
            
        Returns:
            dict or None: 기존 데이터
        """
        try:
            response = self.supabase.table("daily_video_trends").select("*").eq(
                "keyword", keyword
            ).eq(
                "upload_date", upload_date.isoformat()
            ).eq(
                "collected_date", collected_date.isoformat()
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[!] 현재 데이터 조회 중 오류: {e}")
            return None

    def get_latest_trends(self, keyword, limit=30):
        """
        최신 수집 데이터 조회
        
        Args:
            keyword (str): 검색 키워드
            limit (int): 조회할 개수
            
        Returns:
            list: 트렌드 데이터 리스트
        """
        try:
            response = self.supabase.table("daily_video_trends").select("*").eq(
                "keyword", keyword
            ).order(
                "collected_date", desc=True
            ).order(
                "upload_date", desc=True
            ).limit(limit).execute()
            
            return response.data
        except Exception as e:
            print(f"[!] 데이터 조회 중 오류: {e}")
            return []

    def get_upload_date_timeline(self, keyword, upload_date):
        """
        특정 업로드 날짜의 시계열 데이터 조회
        
        Args:
            keyword (str): 검색 키워드
            upload_date (date): 업로드 날짜
            
        Returns:
            list: 시계열 데이터 (수집 날짜별 통계)
        """
        try:
            response = self.supabase.table("daily_video_trends").select("*").eq(
                "keyword", keyword
            ).eq(
                "upload_date", upload_date.isoformat()
            ).order(
                "collected_date", desc=False
            ).execute()
            
            return response.data
        except Exception as e:
            print(f"[!] 시계열 데이터 조회 중 오류: {e}")
            return []

if __name__ == "__main__":
    try:
        db = TrendDatabase()
        
        # 테스트 데이터
        test_data = {
            'keyword': '테스트',
            'upload_date': date(2026, 1, 15),
            'collected_date': date(2026, 1, 22),
            'video_count': 10,
            'total_views': 50000,
            'total_likes': 2000,
            'total_comments': 500,
            'views_growth': 5000,
            'views_growth_rate': 11.11
        }
        
        # 실제로 저장하려면 아래 주석 해제
        # db.save_trend_data(test_data)
        
        print("[✓] 데이터베이스 관리 도구 준비 완료")
    except Exception as e:
        print(f"[!] 오류 발생: {e}")
