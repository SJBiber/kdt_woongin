import os  # 운영체제와 통신하기 위한 도구 (파일 경로, 환경변수 등)
import pandas as pd  # 데이터를 표 형태로 처리하고 통계(합계, 평균)를 내는 도구
from googleapiclient.discovery import build  # 구글 API(유튜브) 서비스를 만들기 위한 도구
from dotenv import load_dotenv  # .env 파일에 저장된 비밀번호(API키)를 읽어오는 도구
from datetime import datetime, timedelta, timezone  # 날짜와 시간을 계산하는 도구
import sys  # 파이썬 시스템 설정 도구
import io  # 입력/출력 데이터를 다루는 도구
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from database import SupabaseManager  # 직접 만든 데이터베이스 관리 도구

# 1. 환경 설정 및 초기화 - config/.env 파일
config_path = PROJECT_ROOT / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

# 한글 출력 깨짐 방지: 표준 출력을 UTF-8 형식으로 재설정합니다.
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class YouTubeTrendCrawler:
    """유튜브 트렌드 데이터를 수집하는 클래스"""
    
    def __init__(self):
        # API 키 가져오기
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("[!] YOUTUBE_API_KEY가 .env 파일에 없습니다. 확인해주세요.")
        
        # 유튜브 API 연결 객체 생성 (버전 v3 사용)
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_metrics_for_period(self, keyword, start_date, end_date):
        """특정 시작일~종료일 사이의 영상 정보를 수집하는 함수"""
        
        # 유튜브 API가 요구하는 시간 형식(2024-01-01T00:00:00Z)으로 변환
        start_time = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_time = end_date.strftime('%Y-%m-%dT23:59:59Z')
        
        video_list = []  # 수집한 데이터를 담을 바구니
        next_page_token = None  # 다음 페이지가 있는지 확인하는 딱지

        while True:
            try:
                # [A] 검색 API 호출: 키워드에 맞는 영상 목록을 검색합니다.
                search_response = self.youtube.search().list(
                    q=keyword,
                    part="id,snippet",
                    publishedAfter=start_time,
                    publishedBefore=end_time,
                    maxResults=50,  # 한 번에 최대 50개씩
                    type="video",
                    order="date",  # 최신순 정렬
                    regionCode="KR",  # 한국 지역
                    relevanceLanguage="ko",  # 한국어 결과 우선
                    pageToken=next_page_token
                ).execute()

                items = search_response.get("items", [])
                if not items:
                    break

                # 검색된 영상들의 ID만 쏙쏙 뽑아냅니다.
                current_batch_ids = [item["id"]["videoId"] for item in items]
                
                # [B] 상세 정보 API 호출: 검색 결과에는 조회수 등이 없어서 다시 물어봐야 합니다.
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet",
                    id=",".join(current_batch_ids)  # ID들을 쉼표로 연결해서 한꺼번에 요청
                ).execute()

                # 상세 정보(조회수, 좋아요, 댓글)를 하나씩 꺼내서 보관합니다.
                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    pub_date = item["snippet"]["publishedAt"][:10]  # 날짜만 추출 (YYYY-MM-DD)
                    video_list.append({
                        "date": pub_date,
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0))
                    })

                # 다음 페이지가 있는지 확인하고, 있으면 계속 돌립니다.
                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
            except Exception as e:
                # 구글 API 사용 한도(할당량)를 다 썼을 때의 처리
                if "quotaExceeded" in str(e):
                    print("\n[알림] 오늘 쓸 수 있는 유튜브 API 할당량을 모두 사용했습니다.")
                    return video_list
                print(f"\n[오류] 기간 수집 중 문제가 생겼습니다: {e}")
                break

        return video_list

    def get_historical_data(self, keyword, total_days=365):
        """긴 기간(365일)을 안전하게(나눠서) 수집하고 통계를 내는 함수"""
        
        # 어제 날짜와 180일 전 날짜 계산
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = end_date - timedelta(days=total_days)
        
        print(f"[*] 전체 분석 시작: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        all_videos = []
        current_end = end_date
        
        # 전체 기간을 30일씩 작게 쪼개서 수집합니다 (데이터 누락 방지!)
        while current_end > start_date:
            current_start = max(start_date, current_end - timedelta(days=30))
            print(f"[*] 수집 중: {current_start.strftime('%Y-%m-%d')} ~ {current_end.strftime('%Y-%m-%d')}...")
            
            period_data = self.get_metrics_for_period(keyword, current_start, current_end)
            all_videos.extend(period_data)
            
            print(f"  -> 현재까지 총 {len(all_videos)}개의 영상을 찾았습니다.")
            
            # 다음 구간(이전 30일)으로 이동
            current_end = current_start - timedelta(days=1)
            
        if not all_videos:
            return None

        # [C] 수집된 방대한 데이터를 Pandas 표로 만듭니다.
        df = pd.DataFrame(all_videos)
        
        # 날짜별(date)로 묶어서 합계를 계산합니다.
        summary_df = df.groupby("date").agg({
            "view_count": ["count", "sum"],  # 영상 개수와 조회수 합계
            "like_count": "sum",             # 좋아요 합계
            "comment_count": "sum"           # 댓글 합계
        }).reset_index()

        # 표의 이름을 보기 좋게 바꿉니다.
        summary_df.columns = ["date", "video_count", "total_views", "total_likes", "total_comments"]
        summary_df["keyword"] = keyword
        
        return summary_df

def main():
    """프로그램의 시작점 (메인 함수)"""
    try:
        # 도구 준비
        crawler = YouTubeTrendCrawler()
        db = SupabaseManager()
        keyword = "임성근 쉐프" 
        
        # 1. 데이터 수집 및 분석 시작
        summary_df = crawler.get_historical_data(keyword, total_days=365)
        
        # 2. 결과가 있으면 데이터베이스(Supabase)에 하나씩 저장
        if summary_df is not None:
            print(f"\n[*] 분석 결과 {len(summary_df)}일치 데이터를 DB에 저장합니다...")
            
            for _, row in summary_df.iterrows():
                db_data = {
                    "date": row["date"],
                    "keyword": row["keyword"],
                    "video_count": int(row["video_count"]),
                    "total_views": int(row["total_views"]),
                    "total_likes": int(row["total_likes"]),
                    "total_comments": int(row["total_comments"])
                }
                db.insert_daily_trend(db_data)  # DB에 쏙!
                
            print("\n[성공] 모든 데이터를 안전하게 저장했습니다.")
        else:
            print("[알림] 수집된 데이터가 없습니다.")
            
    except Exception as e:
        print(f"[오류] 실행 중에 문제가 발생했습니다: {e}")

# 이 파일을 직접 실행했을 때만 main()을 작동시킵니다.
if __name__ == "__main__":
    main()
