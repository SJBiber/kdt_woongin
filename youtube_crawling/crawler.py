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

    def get_bulk_metrics(self, keyword, start_date, end_date):
        """지정된 기간 동안 업로드된 모든 영상의 데이터를 가져와 일별로 집계합니다."""
        start_time = start_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_time = end_date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        
        print(f"[*] 분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print(f"[*] '{keyword}' 키워드로 일괄 검색 시작...")

        video_list = []
        next_page_token = None

        # 1. 기간 내 모든 영상 ID 수집
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

                # 영상 ID 수집 및 기본 정보 저장
                current_batch_ids = [item["id"]["videoId"] for item in items]
                
                # 2. 수집된 ID들의 상세 통계 즉시 가져오기 (50개씩)
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet",
                    id=",".join(current_batch_ids)
                ).execute()

                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    pub_date = item["snippet"]["publishedAt"][:10] # YYYY-MM-DD 만 추출
                    video_list.append({
                        "date": pub_date,
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0))
                    })

                print(f"[+] 누적 수집 영상 수: {len(video_list)}...", end="\r")

                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
            except Exception as e:
                print(f"\n[!] API 호출 중 오류 발생: {e}")
                if "quotaExceeded" in str(e):
                    print("[CRITICAL] API 할당량이 초과되었습니다.")
                    break
                break

        print(f"\n[*] 수집 완료. 총 {len(video_list)}개의 영상을 분석합니다.")
        
        if not video_list:
            return None

        # 3. Pandas를 활용하여 일별 집계
        df = pd.DataFrame(video_list)
        summary_df = df.groupby("date").agg({
            "view_count": ["count", "sum"],
            "like_count": "sum",
            "comment_count": "sum"
        }).reset_index()

        # 컬럼명 정리
        summary_df.columns = ["date", "video_count", "total_views", "total_likes", "total_comments"]
        summary_df["keyword"] = keyword
        
        return summary_df

def main():
    try:
        crawler = YouTubeTrendCrawler()
        db = SupabaseManager()
        keyword = "두쫀쿠"
        
        # 날짜 범위 설정 (6개월 전 ~ 어제)
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = end_date - timedelta(days=180)
        
        summary_df = crawler.get_bulk_metrics(keyword, start_date, end_date)
        
        if summary_df is not None:
            print(f"[*] 총 {len(summary_df)}일치 데이터를 DB에 저장합니다...")
            
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
