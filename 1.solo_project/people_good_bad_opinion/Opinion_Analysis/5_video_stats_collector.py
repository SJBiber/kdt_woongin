"""
YouTube 영상 통계 수집기
- 조회수, 좋아요수를 수집하여 '좋아요 비율(Engagement Rate)'을 계산
- youtube_link.txt에서 영상 링크를 읽어 처리
"""

import logging
import re
import json
import csv
from datetime import datetime
from pathlib import Path
from database.supabase_client import SupabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 논란 기준일
CONTROVERSY_DATE = "2026-01-19"

def extract_video_id(url):
    """YouTube URL에서 video_id 추출"""
    url = url.strip()

    # shorts 형식
    if '/shorts/' in url:
        match = re.search(r'/shorts/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)

    # 일반 watch 형식
    if 'v=' in url:
        match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)

    # youtu.be 형식
    if 'youtu.be/' in url:
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)

    return None

def load_video_links(file_path="youtube_link.txt"):
    """youtube_link.txt에서 영상 링크와 메타정보(날짜, 설명) 로드"""
    links = []
    current_comment = ""

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # 빈 줄 스킵
            if not line:
                continue

            # 주석 처리 (설명 저장)
            if line.startswith('#'):
                # 주석처리된 링크는 스킵
                if 'http' in line or 'youtube' in line.lower():
                    continue
                current_comment = line[1:].strip()
                continue

            # URL인 경우
            if 'youtube.com' in line or 'youtu.be' in line:
                video_id = extract_video_id(line)
                if video_id:
                    # 날짜 추출 시도 (예: "2026 1월 15일", "2025 12월 29일")
                    date_match = re.search(r'(\d{4})\s*(\d{1,2})월\s*(\d{1,2})일', current_comment)
                    upload_date = None
                    if date_match:
                        year, month, day = date_match.groups()
                        upload_date = f"{year}-{int(month):02d}-{int(day):02d}"

                    links.append({
                        'url': line,
                        'video_id': video_id,
                        'description': current_comment,
                        'upload_date': upload_date
                    })
                current_comment = ""

    return links

def fetch_video_stats_yt_dlp(url):
    """yt-dlp를 사용하여 영상 통계 가져오기"""
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return {
                'title': info.get('title', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'comment_count': info.get('comment_count', 0),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),  # YYYYMMDD 형식
                'channel': info.get('channel', 'Unknown'),
            }
    except ImportError:
        logger.error("yt-dlp가 설치되어 있지 않습니다. 'pip install yt-dlp'로 설치해주세요.")
        return None
    except Exception as e:
        logger.error(f"영상 정보 가져오기 실패: {url} - {e}")
        return None

def calculate_engagement_rate(view_count, like_count):
    """좋아요 비율(Engagement Rate) 계산"""
    if view_count == 0:
        return 0
    return (like_count / view_count) * 100

def collect_all_video_stats():
    """모든 영상의 통계 수집"""
    links = load_video_links()
    logger.info(f"총 {len(links)}개의 영상 링크를 로드했습니다.")

    results = []

    for i, link_info in enumerate(links, 1):
        url = link_info['url']
        logger.info(f"[{i}/{len(links)}] 수집 중: {link_info['description'][:30]}...")

        stats = fetch_video_stats_yt_dlp(url)

        if stats:
            # 업로드 날짜 정리 (yt-dlp는 YYYYMMDD 형식)
            upload_date = link_info.get('upload_date')
            if not upload_date and stats.get('upload_date'):
                raw_date = stats['upload_date']
                if len(raw_date) == 8:
                    upload_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"

            # 논란 전/후 판단
            is_before_controversy = None
            if upload_date:
                is_before_controversy = upload_date < CONTROVERSY_DATE

            engagement_rate = calculate_engagement_rate(
                stats['view_count'],
                stats['like_count']
            )

            result = {
                'video_id': link_info['video_id'],
                'url': url,
                'title': stats['title'],
                'description': link_info['description'],
                'channel': stats['channel'],
                'upload_date': upload_date,
                'is_before_controversy': is_before_controversy,
                'view_count': stats['view_count'],
                'like_count': stats['like_count'],
                'comment_count': stats['comment_count'],
                'duration_sec': stats['duration'],
                'engagement_rate': round(engagement_rate, 4),  # 좋아요/조회수 * 100
            }
            results.append(result)

            logger.info(f"  → 조회수: {stats['view_count']:,} | 좋아요: {stats['like_count']:,} | 비율: {engagement_rate:.2f}%")
        else:
            logger.warning(f"  → 수집 실패: {url}")

    return results

def save_results(results, json_path="video_stats_results.json", csv_path="video_stats_results.csv"):
    """결과를 JSON 및 CSV 파일로 저장"""
    # JSON 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"결과가 JSON 파일로 저장되었습니다: {json_path}")

    # CSV 저장
    if results:
        fieldnames = results[0].keys()
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"결과가 CSV 파일로 저장되었습니다: {csv_path}")

def print_analysis_summary(results):
    """분석 요약 출력"""
    if not results:
        logger.warning("분석할 데이터가 없습니다.")
        return

    print("\n" + "="*70)
    print("📊 영상 통계 분석 요약")
    print("="*70)

    # 논란 전/후 분리
    before = [r for r in results if r.get('is_before_controversy') == True]
    after = [r for r in results if r.get('is_before_controversy') == False]
    unknown = [r for r in results if r.get('is_before_controversy') is None]

    print(f"\n📅 논란 기준일: {CONTROVERSY_DATE}")
    print(f"   - 논란 전 영상: {len(before)}개")
    print(f"   - 논란 후 영상: {len(after)}개")
    print(f"   - 날짜 미상: {len(unknown)}개")

    def calc_stats(data, label):
        if not data:
            return
        total_views = sum(r['view_count'] for r in data)
        total_likes = sum(r['like_count'] for r in data)
        avg_engagement = sum(r['engagement_rate'] for r in data) / len(data)
        overall_engagement = (total_likes / total_views * 100) if total_views > 0 else 0

        print(f"\n{'🟢' if '전' in label else '🔴'} {label}")
        print(f"   총 조회수: {total_views:,}")
        print(f"   총 좋아요: {total_likes:,}")
        print(f"   전체 좋아요 비율: {overall_engagement:.2f}%")
        print(f"   영상별 평균 비율: {avg_engagement:.2f}%")

    calc_stats(before, "논란 전 (호감 여론)")
    calc_stats(after, "논란 후 (비난 여론)")

    # 개별 영상 목록
    print("\n" + "-"*70)
    print("📋 개별 영상 상세")
    print("-"*70)

    for r in sorted(results, key=lambda x: x.get('upload_date') or ''):
        status = "🟢" if r.get('is_before_controversy') else "🔴" if r.get('is_before_controversy') == False else "⚪"
        print(f"\n{status} [{r.get('upload_date', '날짜미상')}] {r['title'][:40]}...")
        print(f"   채널: {r['channel']}")
        print(f"   조회수: {r['view_count']:,} | 좋아요: {r['like_count']:,}")
        print(f"   📈 Engagement Rate: {r['engagement_rate']:.2f}%")

def main():
    logger.info("=== YouTube 영상 통계 수집 시작 ===")

    results = collect_all_video_stats()

    if results:
        save_results(results)
        
        # DB 저장 시도
        db = SupabaseManager()
        if db.client:
            logger.info("데이터베이스(Supabase)에 저장을 시작합니다...")
            db.upsert_video_stats(results)
        else:
            logger.warning("Supabase 설정이 없어 DB 저장을 건너뜁니다.")
            
        print_analysis_summary(results)
    else:
        logger.error("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
