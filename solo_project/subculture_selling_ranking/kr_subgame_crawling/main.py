import os
import time
from scrapers.market import MarketScraper
from scrapers.trend import TrendScraper
from scrapers.youtube import YouTubeScraper
from scrapers.community import CommunityScraper
from utils.db import upsert_game_data
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def main():
    print("동적 서브컬쳐 시장 크롤러 시작 중...")
    
    # 1. 스크래퍼 초기화
    market = MarketScraper(headless=True)
    trend = TrendScraper()
    youtube = YouTubeScraper()
    community = CommunityScraper()
    
    # 2. 동적 타겟 게임 추출
    # 구글 플레이 스토어에서 매출 상위 5개 게임 가져오기
    print("구글 플레이 스토어에서 매출 상위 5개 게임 수집 중...")
    top_rankings = market.get_google_play_rankings(limit=5)
    
    if not top_rankings:
        print("순위 정보 수집 실패. 기존 고정 리스트를 사용합니다.")
        target_games = [
            {"title": "블루 아카이브", "arca_channel": "bluearchive"},
            {"title": "승리의 여신: 니케", "arca_channel": "nikke"}
        ]
    else:
        print(f"감지된 상위 {len(top_rankings)}개 게임: {[g['title'] for g in top_rankings]}")
        target_games = []
        for g in top_rankings:
            # 게임 제목을 기반으로 아카라이브 채널 이름 유추 (공백 제거 및 소문자화)
            # 운영 환경에서는 매핑 테이블을 사용하는 것이 정확합니다.
            game_title = g["title"]
            
            target_games.append({
                "title": game_title,
                "arca_channel": game_title.replace(" ", "").lower()
            })
    
    # 3. 타겟 게임별 상세 데이터 수집
    for game in target_games:
        game_title = game["title"]
        print(f"\n>>> 조사 대상: {game_title}")
        
        # 트렌드 데이터 (네이버 & 구글)
        print(f"  - 검색 트렌드 수집 중...")
        naver_data = trend.get_naver_trend(game_title)
        google_data = trend.get_google_trend(game_title)
        
        # 유튜브 데이터
        print(f"  - 유튜브 지표 수집 중...")
        try:
            yt_data = youtube.get_video_stats(game_title)
        except Exception as e:
            print(f"    유튜브 오류 발생: {e}")
            yt_data = None
            
        # 커뮤니티 데이터 (아카라이브)
        print(f"  - 커뮤니티 여론 수집 중...")
        arca_posts = community.get_arcalive_best(game["arca_channel"])
        
        # 4. 수집 결과 요약 출력
        combined_stats = {
            "게임명": game_title,
            "수집일자": time.strftime("%Y-%m-%d"),
            "네이버검색지수": naver_data[-1]["ratio"] if naver_data else "정보 없음",
            "유튜브업로드수(24h)": yt_data["upload_count_24h"] if yt_data else "정보 없음",
            "아카라이브언급수": len(arca_posts)
        }
        
        print(f"  [요약 결과] {combined_stats}")
        if yt_data and yt_data.get("top_videos"):
            print(f"  [유튜브 인기 영상] {yt_data['top_videos'][0]['title']} (조회수: {yt_data['top_videos'][0]['view_count']})")
            
        # 5. DB 저장 (필요 시 주석 해제)
        # upsert_game_data("game_daily_stats", [combined_stats])

    print("\n크롤링 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
