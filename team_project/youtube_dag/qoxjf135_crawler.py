from airflow.models import Variable  # Airflow 저장 변수 가져오는 도구
from googleapiclient.discovery import build  # 구글 서비스(유튜브) 사용 도구
import pandas as pd  # 데이터 표 형태 처리 도구
from datetime import datetime, timedelta, timezone  # 날짜와 시간 계산 도구
##
class YouTubeTrendCrawler:
   
    def __init__(self):
        # 1. Airflow 관리자 화면 설정 'QOXJF135_YOUTUBE_API_KEY' 변수 가져옴
        #    유튜브 데이터 사용 위한 '출입증' 역할
        self.api_key = Variable.get("QOXJF135_YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("[!] Airflow Variable 'QOXJF135_YOUTUBE_API_KEY' 없음. 설정 확인 필요.")
        
        # 2. 유튜브 API 서비스 연결 (버전 3 사용)
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_metrics_for_period(self, keyword, start_date, end_date):
        """특정 날짜 범위(시작일~종료일) 동안의 영상 정보(조회수 등)를 가져오는 함수"""
        
        # 유튜브 API 시간 형식(예: 2024-01-01T00:00:00Z)으로 날짜 변경
        start_time = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_time = end_date.strftime('%Y-%m-%dT23:59:59Z')
        
        video_list = []  # 수집 데이터 담는 바구니
        next_page_token = None  # 검색 결과 많을 때 다음 페이지 가리키는 포인터

        while True:
            try:
                # [A] 검색 API 호출: 키워드 부합 영상 목록 찾음
                search_response = self.youtube.search().list(
                    q=keyword,
                    part="id,snippet",
                    publishedAfter=start_time,
                    publishedBefore=end_time,
                    maxResults=50,  # 테스트용 조회 개수 1개 제한 (기존 50)
                    type="video",
                    order="date",  # 최신순
                    regionCode="KR",  # 한국 지역
                    relevanceLanguage="ko",  # 한국어 우선
                    pageToken=next_page_token
                ).execute()

                items = search_response.get("items", [])
                if not items:
                    break

                # 검색 영상 고유 ID만 추출
                current_batch_ids = [item["id"]["videoId"] for item in items]
                
                # [B] 상세 정보 API 호출: 검색 결과에 조회수 없어서 별도 요청
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet",
                    id=",".join(current_batch_ids)  # 여러 ID 쉼표 연결해 일괄 요청
                ).execute()
                
                # 조회수, 좋아요, 댓글 수 차례로 바구니에 담음
                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    pub_date = item["snippet"]["publishedAt"][:10]  # 날짜 추출 (YYYY-MM-DD)
                    video_list.append({
                        "date": pub_date,
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0))
                    })

                # 다음 페이지 존재 여부 확인 후 진행
                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
            except Exception as e:
                # API 사용 한도(할당량) 초과 시 처리
                if "quotaExceeded" in str(e):
                    print("[알림] 금일 유튜브 API 할당량 소진됨")
                    return video_list
                print(f"[오류] 데이터 수집 중 문제 발생: {e}")
                break

        return video_list

    def get_historical_data(self, keyword, start_date=None, end_date=None):
        """전체 기간을 분석하고 일별로 합산된 통계 데이터를 만드는 함수 (Upsert용)"""
        
        # 1. 종료일 설정: 날짜 설정 없으면 '어제' 기준
        #    영상 통계 실시간 변동 고려, 어제까지 데이터 매일 갱신
        if end_date is None:
            end_date = datetime.now(timezone.utc) - timedelta(days=1)
            
        # 2. 시작일 설정: 날짜 설정 없으면 '2025-07-17' 고정 날짜 사용
        #    시작일부터 어제까지 모든 데이터 재수집해 최신 지표 반영
        if start_date is None:
            start_date = datetime(2025, 7, 17, tzinfo=timezone.utc)
        
        print(f"[*] 분석 시작 범위: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} (전체 통계 갱신함)")
        
        all_videos = []
        current_end = end_date
        
        # 유튜브 검색 제한 회피 위해 30일 단위 수집
        while current_end >= start_date:
            current_start = max(start_date, current_end - timedelta(days=30))
            print(f"[*] 기간 수집 중: {current_start.strftime('%Y-%m-%d')} ~ {current_end.strftime('%Y-%m-%d')}...")
            
            period_data = self.get_metrics_for_period(keyword, current_start, current_end)
            all_videos.extend(period_data)
            
            current_end = current_start - timedelta(days=1)
            
        if not all_videos:
            return None

        # [C] 수집 영상 데이터 표(DataFrame) 변환 후 분석
        df = pd.DataFrame(all_videos)
        
        # 동일 날짜 그룹화(groupby) 후 총 영상 수, 조회수 등 계산
        summary_df = df.groupby("date").agg({
            "view_count": ["count", "sum"],
            "like_count": "sum",
            "comment_count": "sum"
        }).reset_index()

        # 표 컬럼명 변경
        summary_df.columns = ["date", "video_count", "total_views", "total_likes", "total_comments"]
        summary_df["keyword"] = keyword
        
        return summary_df
