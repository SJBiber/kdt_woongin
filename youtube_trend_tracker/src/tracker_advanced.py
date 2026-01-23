import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone, date
import sys
import io
from pathlib import Path
from src.database import TrendDatabase
import time

# 환경 설정 - config/.env 파일 로드
config_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

# 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class AdvancedTrendTracker:
    """YouTube 트렌드 추적 크롤러 (API 키 자동 전환 기능 포함)"""
    
    def __init__(self):
        # 여러 API 키 로드
        self.api_keys = []
        key_index = 1
        while True:
            key = os.getenv(f"YOUTUBE_API_KEY_{key_index}")
            if not key:
                break
            self.api_keys.append(key)
            key_index += 1
        
        if not self.api_keys:
            raise ValueError("[!] YOUTUBE_API_KEY_1이 .env 파일에 없습니다.")
        
        self.current_key_index = 0
        self.youtube = build("youtube", "v3", developerKey=self.api_keys[self.current_key_index])
        self.db = TrendDatabase()
        
        print(f"[✓] YouTube API 연결 성공 (사용 가능한 키: {len(self.api_keys)}개)")

    def switch_api_key(self):
        """다음 API 키로 전환"""
        if len(self.api_keys) <= 1:
            print("[!] 더 이상 사용 가능한 API 키가 없습니다.")
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.youtube = build("youtube", "v3", developerKey=self.api_keys[self.current_key_index])
        print(f"[🔄] API 키 전환 완료 (키 #{self.current_key_index + 1})")
        return True

    def search_videos_by_upload_date(self, keyword, upload_date, retry_count=0):
        """
        특정 날짜에 업로드된 영상 검색 (API 키 자동 전환 포함)
        
        Args:
            keyword (str): 검색 키워드
            upload_date (date): 업로드 날짜
            retry_count (int): 재시도 횟수
            
        Returns:
            list: 영상 정보 리스트
        """
        # 해당 날짜의 시작과 끝 시간
        start_time = datetime.combine(upload_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_time = datetime.combine(upload_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        videos = []
        next_page_token = None
        
        try:
            while True:
                # 검색 API 호출
                search_response = self.youtube.search().list(
                    q=keyword,
                    part="id,snippet",
                    publishedAfter=start_str,
                    publishedBefore=end_str,
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

                # 영상 ID 추출
                video_ids = [item["id"]["videoId"] for item in items]
                
                # 상세 정보 조회
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet",
                    id=",".join(video_ids)
                ).execute()

                # 통계 수집
                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    videos.append({
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0))
                    })

                # 다음 페이지 확인
                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
                    
                # API 호출 제한 방지
                time.sleep(0.5)
                
        except Exception as e:
            if "quotaExceeded" in str(e):
                print(f"[!] API 할당량 초과 (키 #{self.current_key_index + 1})")
                
                # API 키 전환 시도
                if retry_count < len(self.api_keys) - 1:
                    if self.switch_api_key():
                        print(f"[↻] 재시도 중...")
                        time.sleep(1)
                        return self.search_videos_by_upload_date(keyword, upload_date, retry_count + 1)
                
                print(f"[!] 모든 API 키의 할당량이 소진되었습니다.")
                raise
            else:
                print(f"[!] 검색 중 오류: {e}")
        
        return videos

    def calculate_growth(self, current_stats, previous_stats):
        """
        증가량 및 증가율 계산
        
        Args:
            current_stats (dict): 현재 통계
            previous_stats (dict or None): 전날 통계
            
        Returns:
            dict: 증가량 및 증가율 정보
        """
        if not previous_stats:
            return {
                'views_growth': 0,
                'likes_growth': 0,
                'comments_growth': 0,
                'views_growth_rate': 0.0,
                'likes_growth_rate': 0.0,
                'comments_growth_rate': 0.0
            }
        
        views_growth = current_stats['total_views'] - previous_stats['total_views']
        likes_growth = current_stats['total_likes'] - previous_stats['total_likes']
        comments_growth = current_stats['total_comments'] - previous_stats['total_comments']
        
        # 증가율 계산 (0으로 나누기 방지)
        views_growth_rate = (views_growth / previous_stats['total_views'] * 100) if previous_stats['total_views'] > 0 else 0
        likes_growth_rate = (likes_growth / previous_stats['total_likes'] * 100) if previous_stats['total_likes'] > 0 else 0
        comments_growth_rate = (comments_growth / previous_stats['total_comments'] * 100) if previous_stats['total_comments'] > 0 else 0
        
        return {
            'views_growth': views_growth,
            'likes_growth': likes_growth,
            'comments_growth': comments_growth,
            'views_growth_rate': round(views_growth_rate, 2),
            'likes_growth_rate': round(likes_growth_rate, 2),
            'comments_growth_rate': round(comments_growth_rate, 2)
        }

    def track_date_range(self, keyword, start_date, end_date):
        """
        특정 날짜 범위의 영상들의 현재 통계 수집 및 저장
        
        Args:
            keyword (str): 검색 키워드
            start_date (date): 시작 날짜 (포함)
            end_date (date): 종료 날짜 (포함)
        """
        collected_date = date.today()
        
        # 날짜 범위 계산
        total_days = (end_date - start_date).days + 1
        
        print(f"\n{'='*60}")
        print(f"[*] 트렌드 추적 시작")
        print(f"    키워드: {keyword}")
        print(f"    수집 날짜: {collected_date}")
        print(f"    수집 범위: {start_date} ~ {end_date}")
        print(f"    총 {total_days}일")
        print(f"    사용 가능한 API 키: {len(self.api_keys)}개")
        print(f"{'='*60}\n")
        
        success_count = 0
        error_count = 0
        
        # 날짜 범위 순회
        current_date = start_date
        day_num = 1
        
        while current_date <= end_date:
            upload_date = current_date
            
            try:
                print(f"[{day_num}/{total_days}] 처리 중: {upload_date} 업로드 영상...")
                
                # 해당 날짜에 업로드된 영상 검색
                videos = self.search_videos_by_upload_date(keyword, upload_date)
                
                if not videos:
                    print(f"  → 영상 없음")
                    current_date += timedelta(days=1)
                    day_num += 1
                    continue
                
                # 현재 통계 집계
                current_stats = {
                    'keyword': keyword,
                    'upload_date': upload_date,
                    'collected_date': collected_date,
                    'video_count': len(videos),
                    'total_views': sum(v['views'] for v in videos),
                    'total_likes': sum(v['likes'] for v in videos),
                    'total_comments': sum(v['comments'] for v in videos)
                }
                
                # 전날 데이터 조회
                previous_data = self.db.get_previous_day_data(
                    keyword, upload_date, collected_date
                )
                
                # 증가량 계산
                growth_data = self.calculate_growth(current_stats, previous_data)
                current_stats.update(growth_data)
                
                # DB 저장
                self.db.save_trend_data(current_stats)
                
                success_count += 1
                
                # 증가량 표시
                if previous_data:
                    print(f"  → 영상: {len(videos)}개 | "
                          f"조회수: {current_stats['total_views']:,} "
                          f"(+{growth_data['views_growth']:,}, {growth_data['views_growth_rate']:+.1f}%)")
                else:
                    print(f"  → 영상: {len(videos)}개 | "
                          f"조회수: {current_stats['total_views']:,} (첫 수집)")
                
                # API 호출 제한 방지
                time.sleep(1)
                
            except Exception as e:
                if "quotaExceeded" in str(e) or "모든 API 키" in str(e):
                    print(f"\n[!] 모든 API 키의 할당량이 소진되었습니다.")
                    print(f"[!] {upload_date}부터 내일 다시 실행하세요.")
                    break
                error_count += 1
                print(f"  → 오류 발생: {e}")
            
            current_date += timedelta(days=1)
            day_num += 1
        
        print(f"\n{'='*60}")
        print(f"[✓] 트렌드 추적 완료")
        print(f"    성공: {success_count}일")
        print(f"    실패: {error_count}일")
        print(f"{'='*60}\n")

def main():
    """메인 함수"""
    try:
        tracker = AdvancedTrendTracker()
        
        # 설정
        keyword = "임성근 쉐프"
        lookback_days = 30  # 기본값
        
        # 트렌드 추적 실행
        today = date.today()
        start_date = today - timedelta(days=lookback_days)
        tracker.track_date_range(keyword, start_date, today - timedelta(days=1))
        
    except Exception as e:
        print(f"[!] 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
