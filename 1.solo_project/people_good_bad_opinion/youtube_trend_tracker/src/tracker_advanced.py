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
        self.exhausted_keys = set() # 실패한 키 인덱스 추적
        self.youtube = build("youtube", "v3", developerKey=self.api_keys[self.current_key_index])
        self.db = TrendDatabase()
        
        print(f"[✓] YouTube API 연결 성공 (사용 가능한 키: {len(self.api_keys)}개)")

    def switch_api_key(self):
        """다음 API 키로 전환"""
        self.exhausted_keys.add(self.current_key_index)
        
        if len(self.exhausted_keys) >= len(self.api_keys):
            print("[!] 모든 API 키가 소진되었습니다.")
            return False
        
        # 아직 시도해보지 않은 키를 찾아서 전환
        start_index = self.current_key_index
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            if self.current_key_index not in self.exhausted_keys:
                self.youtube = build("youtube", "v3", developerKey=self.api_keys[self.current_key_index])
                print(f"[🔄] API 키 전환 완료 (키 #{self.current_key_index + 1})")
                return True
        
        return False

    def search_videos_by_time_range(self, keyword, start_time, end_time, retry_count=0, depth=0):
        """
        특정 시간 범위에 업로드된 영상 검색 (재귀적 시간 분할 포함)
        
        Args:
            keyword (str): 검색 키워드
            start_time (datetime): 시작 시간 (UTC)
            end_time (datetime): 종료 시간 (UTC)
            retry_count (int): 재시도 횟수
            depth (int): 재귀 깊이
            
        Returns:
            list: 영상 정보 리스트
        """
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        videos = []
        next_page_token = None
        page_count = 0
        max_pages = 20  # 최대 20페이지 (1000개 제한)
        
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
                page_count += 1
                
                # 페이지 제한에 도달하면 시간 범위를 분할
                if page_count >= max_pages and next_page_token:
                    if depth < 3:  # 최대 3단계까지 분할 (6시간 -> 3시간 -> 1.5시간)
                        print(f"  ⚠️  결과가 많아 시간 범위를 분할합니다 (깊이: {depth+1})")
                        
                        # 시간 범위를 반으로 분할
                        mid_time = start_time + (end_time - start_time) / 2
                        
                        # 전반부 검색
                        videos_first = self.search_videos_by_time_range(
                            keyword, start_time, mid_time, retry_count, depth + 1
                        )
                        time.sleep(0.5)
                        
                        # 후반부 검색
                        videos_second = self.search_videos_by_time_range(
                            keyword, mid_time, end_time, retry_count, depth + 1
                        )
                        
                        # 중복 제거 후 병합
                        all_videos = videos + videos_first + videos_second
                        seen_ids = set()
                        unique_videos = []
                        for v in all_videos:
                            if v['video_id'] not in seen_ids:
                                seen_ids.add(v['video_id'])
                                unique_videos.append(v)
                        
                        return unique_videos
                    else:
                        print(f"  ⚠️  최대 분할 깊이 도달, 일부 영상이 누락될 수 있습니다")
                        break
                
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
                        return self.search_videos_by_time_range(
                            keyword, start_time, end_time, retry_count + 1, depth
                        )
                
                print(f"[!] 모든 API 키의 할당량이 소진되었습니다.")
                raise
            else:
                print(f"[!] 검색 중 오류: {e}")
        
        return videos

    def search_videos_by_upload_date(self, keyword, upload_date, retry_count=0):
        """
        특정 날짜에 업로드된 영상 검색 (6시간 단위로 분할)
        
        Args:
            keyword (str): 검색 키워드
            upload_date (date): 업로드 날짜
            retry_count (int): 재시도 횟수
            
        Returns:
            list: 영상 정보 리스트
        """
        all_videos = []
        
        # 하루를 6시간씩 4개 구간으로 분할
        time_ranges = [
            (0, 6),   # 00:00 - 06:00
            (6, 12),  # 06:00 - 12:00
            (12, 18), # 12:00 - 18:00
            (18, None)  # 18:00 - 다음날 00:00
        ]
        
        for start_hour, end_hour in time_ranges:
            start_time = datetime.combine(upload_date, datetime.min.time()).replace(
                hour=start_hour, tzinfo=timezone.utc
            )
            
            # 마지막 구간은 다음 날 00:00으로 설정
            if end_hour is None:
                end_time = datetime.combine(upload_date + timedelta(days=1), datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
            else:
                end_time = datetime.combine(upload_date, datetime.min.time()).replace(
                    hour=end_hour, tzinfo=timezone.utc
                )
            
            videos = self.search_videos_by_time_range(keyword, start_time, end_time, retry_count)
            all_videos.extend(videos)
            
            time.sleep(0.3)  # 구간 사이 대기
        
        # 중복 제거
        seen_ids = set()
        unique_videos = []
        for v in all_videos:
            if v['video_id'] not in seen_ids:
                seen_ids.add(v['video_id'])
                unique_videos.append(v)
        
        return unique_videos

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

        최적화 방식:
          1단계: 일별 루프로 검색 (6시간 분할/재귀 없이 단순 페이징)
                 → 일별 40~60개 영상도 누락 없이 수집
          2단계: 전체 영상 ID를 50개씩 배치로 통계 조회
          3단계: 업로드 날짜별 집계 후 DB 저장

        Args:
            keyword (str): 검색 키워드
            start_date (date): 시작 날짜 (포함)
            end_date (date): 종료 날짜 (포함)
        """
        from collections import defaultdict
        
        # 수집 시작 시 소진된 키 목록 초기화 (오늘의 할당량 확인을 위해)
        self.exhausted_keys = set()
        
        collected_date = date.today()
        total_days = (end_date - start_date).days + 1
        api_call_count = 0

        print(f"\n{'='*60}")
        print(f"[*] 트렌드 추적 시작 (최적화 모드)")
        print(f"    키워드: {keyword}")
        print(f"    수집 날짜: {collected_date}")
        print(f"    수집 범위: {start_date} ~ {end_date} ({total_days}일)")
        print(f"    사용 가능한 API 키: {len(self.api_keys)}개")
        print(f"{'='*60}\n")

        # ── Step 1: 일별 루프로 검색 (단순 페이징만, 6시간 분할 없음) ──
        #   일별 40~60개 영상 → 페이지 1~2회면 충분 (500개 제한 안전)
        print("[1/3] 일별 영상 목록 검색 중...")

        all_video_ids = []
        video_publish_dates = {}  # video_id -> "YYYY-MM-DD"

        current_date = start_date
        day_num = 1

        while current_date <= end_date:
            day_start_str = datetime.combine(current_date, datetime.min.time()).replace(
                tzinfo=timezone.utc
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
            day_end_str = (datetime.combine(current_date + timedelta(days=1), datetime.min.time()).replace(
                tzinfo=timezone.utc
            ) - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

            next_page_token = None
            day_count = 0

            while True:
                try:
                    search_response = self.youtube.search().list(
                        q=keyword,
                        part="id,snippet",
                        publishedAfter=day_start_str,
                        publishedBefore=day_end_str,
                        maxResults=50,
                        type="video",
                        order="date",
                        regionCode="KR",
                        relevanceLanguage="ko",
                        pageToken=next_page_token
                    ).execute()
                    api_call_count += 1

                    items = search_response.get("items", [])
                    if not items:
                        break

                    for item in items:
                        vid = item["id"]["videoId"]
                        published = item["snippet"]["publishedAt"][:10]
                        if vid not in video_publish_dates:
                            all_video_ids.append(vid)
                            video_publish_dates[vid] = published
                            day_count += 1

                    next_page_token = search_response.get("nextPageToken")
                    if not next_page_token:
                        break

                    time.sleep(0.3)

                except Exception as e:
                    if "quotaExceeded" in str(e):
                        print(f"[!] API 할당량 초과 (키 #{self.current_key_index + 1})")
                        if not self.switch_api_key():
                            print(f"[!] 모든 API 키의 할당량이 소진되었습니다.")
                            print(f"[!] {current_date}부터 내일 다시 실행하세요.")
                            raise
                        continue
                    raise

            if day_count > 0:
                print(f"  [{day_num}/{total_days}] {current_date}: {day_count}개 영상")
            else:
                print(f"  [{day_num}/{total_days}] {current_date}: 영상 없음")

            current_date += timedelta(days=1)
            day_num += 1
            time.sleep(0.2)

        print(f"  ✓ 검색 완료: 총 {len(all_video_ids)}개 영상 (API {api_call_count}회)")

        if not all_video_ids:
            print("[!] 검색 결과가 없습니다.")
            return

        # ── Step 2: 전체 영상 ID를 배치로 통계 조회 (50개씩) ──
        print(f"\n[2/3] 영상 통계 일괄 조회 중 ({len(all_video_ids)}개)...")

        all_videos = []
        stats_call_count = 0

        for i in range(0, len(all_video_ids), 50):
            batch_ids = all_video_ids[i:i+50]

            try:
                stats_response = self.youtube.videos().list(
                    part="statistics",
                    id=",".join(batch_ids)
                ).execute()
                api_call_count += 1
                stats_call_count += 1

                for item in stats_response.get("items", []):
                    stats = item["statistics"]
                    vid = item["id"]
                    all_videos.append({
                        "video_id": vid,
                        "upload_date": video_publish_dates.get(vid, "unknown"),
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0))
                    })

            except Exception as e:
                if "quotaExceeded" in str(e):
                    print(f"[!] API 할당량 초과 (키 #{self.current_key_index + 1})")
                    if not self.switch_api_key():
                        print(f"[!] 모든 API 키의 할당량이 소진되었습니다.")
                        raise
                    continue
                print(f"  → 통계 조회 오류: {e}")

            print(f"  → {min(i+50, len(all_video_ids))}/{len(all_video_ids)} 처리 완료")
            time.sleep(0.3)

        print(f"  ✓ 통계 조회 완료 (API {stats_call_count}회)")

        # ── Step 3: 업로드 날짜별 집계 및 저장 ──
        print(f"\n[3/3] 날짜별 집계 및 저장 중...")

        date_groups = defaultdict(list)
        for video in all_videos:
            date_groups[video['upload_date']].append(video)

        success_count = 0
        error_count = 0

        for upload_date_str in sorted(date_groups.keys()):
            videos = date_groups[upload_date_str]

            try:
                upload_dt = date.fromisoformat(upload_date_str)
            except ValueError:
                print(f"  → 날짜 파싱 오류: {upload_date_str}, 건너뜀")
                error_count += 1
                continue

            current_stats = {
                'keyword': keyword,
                'upload_date': upload_dt,
                'collected_date': collected_date,
                'video_count': len(videos),
                'total_views': sum(v['views'] for v in videos),
                'total_likes': sum(v['likes'] for v in videos),
                'total_comments': sum(v['comments'] for v in videos)
            }

            # 전날 데이터 조회
            previous_data = self.db.get_previous_day_data(
                keyword, upload_dt, collected_date
            )

            # 증가량 계산
            growth_data = self.calculate_growth(current_stats, previous_data)
            current_stats.update(growth_data)

            # DB 저장 (기존 데이터와 video_count 비교)
            existing_data = self.db.get_current_data(keyword, upload_dt, collected_date)
            
            if existing_data:
                old_count = existing_data.get('video_count', 0)
                if old_count > current_stats['video_count']:
                    print(f"  → [{upload_date_str}] 건너뜀: 기존 데이터의 영상 수({old_count}개)가 현재({current_stats['video_count']}개)보다 많음")
                    continue
                else:
                    print(f"  → [{upload_date_str}] 업데이트: 기존({old_count}개) -> 현재({current_stats['video_count']}개)")

            # DB 저장
            self.db.save_trend_data(current_stats)
            success_count += 1

            # 증가량 표시
            if previous_data:
                print(f"  [{upload_date_str}] 영상: {len(videos)}개 | "
                      f"조회수: {current_stats['total_views']:,} "
                      f"(+{growth_data['views_growth']:,}, {growth_data['views_growth_rate']:+.1f}%)")
            else:
                print(f"  [{upload_date_str}] 영상: {len(videos)}개 | "
                      f"조회수: {current_stats['total_views']:,} (첫 수집)")

        print(f"\n{'='*60}")
        print(f"[✓] 트렌드 추적 완료")
        print(f"    검색된 영상: {len(all_videos)}개")
        print(f"    저장된 날짜: {success_count}일")
        print(f"    오류: {error_count}일")
        print(f"    총 API 호출: {api_call_count}회")
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
