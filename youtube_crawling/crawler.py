import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import sys
import io
from database import SupabaseManager

# .env 파일 로드
load_dotenv()

# 표준 출력을 UTF-8로 재설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class YouTubeTrendCrawler:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("[!] YOUTUBE_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_metrics_for_period(self, keyword, start_date, end_date):
        """특정 기간 동안 업로드된 영상 데이터를 가져옵니다."""
        # RFC 3339 규격에 맞춰 'Z' 포맷 사용 (유튜브 API 권장)
        start_time = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_time = end_date.strftime('%Y-%m-%dT23:59:59Z')
        
        video_list = []
        next_page_token = None

        while True:
            try:
                search_response = self.youtube.search().list(
                    q=keyword,
                    part="id,snippet",
                    publishedAfter=start_time,
                    publishedBefore=end_time,
                    maxResults=50,
                    type="video",
                    order="date",
                    regionCode="KR",
                    relevanceLanguage="ko",
                    pageToken=next_page_token
                ).execute()

                items = search_response.get("items", [])
                if not items:
                    break

                # 영상 ID 수집
                current_batch_ids = [item["id"]["videoId"] for item in items]
                
                # 상세 통계 가져오기
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet",
                    id=",".join(current_batch_ids)
                ).execute()

                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    pub_date = item["snippet"]["publishedAt"][:10]
                    video_list.append({
                        "date": pub_date,
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0))
                    })

                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
            except Exception as e:
                if "quotaExceeded" in str(e):
                    print("\n[CRITICAL] API 할당량이 초과되었습니다.")
                    return video_list
                print(f"\n[!] 기간 수집 중 오류: {e}")
                break

        return video_list

    def get_historical_data(self, keyword, total_days=180):
        """전체 기간을 30일 단위로 나누어 누락을 방지하며 수집합니다."""
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = end_date - timedelta(days=total_days)
        
        print(f"[*] 전체 분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        all_videos = []
        current_end = end_date
        
        while current_end > start_date:
            current_start = max(start_date, current_end - timedelta(days=30))
            print(f"[*] 데이터 확보 중: {current_start.strftime('%Y-%m-%d')} ~ {current_end.strftime('%Y-%m-%d')}...")
            
            period_data = self.get_metrics_for_period(keyword, current_start, current_end)
            all_videos.extend(period_data)
            
            print(f"  -> 현재까지 총 {len(all_videos)}개 영상 식별됨")
            
            # 다음 30일 구간으로 이동
            current_end = current_start - timedelta(days=1)
            
        if not all_videos:
            return None

        # Pandas를 활용하여 일별 집계
        df = pd.DataFrame(all_videos)
        summary_df = df.groupby("date").agg({
            "view_count": ["count", "sum"],
            "like_count": "sum",
            "comment_count": "sum"
        }).reset_index()

        summary_df.columns = ["date", "video_count", "total_views", "total_likes", "total_comments"]
        summary_df["keyword"] = keyword
        
        return summary_df

def main():
    try:
        crawler = YouTubeTrendCrawler()
        db = SupabaseManager()
        keyword = "두바이 쫀득 쿠키" # "두쫀쿠"보다 더 정확한 검색을 위해 풀네임 권장
        
        # 180일치 데이터 수집 시작
        summary_df = crawler.get_historical_data(keyword, total_days=180)
        
        if summary_df is not None:
            print(f"\n[*] 총 {len(summary_df)}일치 데이터를 DB에 저장합니다...")
            
            for _, row in summary_df.iterrows():
                db_data = {
                    "date": row["date"],
                    "keyword": row["keyword"],
                    "video_count": int(row["video_count"]),
                    "total_views": int(row["total_views"]),
                    "total_likes": int(row["total_likes"]),
                    "total_comments": int(row["total_comments"])
                }
                db.insert_daily_trend(db_data)
                
            print("\n[!] 모든 데이터 적재가 완료되었습니다.")
        else:
            print("[!] 수집된 데이터가 없습니다.")
            
    except Exception as e:
        print(f"[!] 오류 발생: {e}")

if __name__ == "__main__":
    main()
