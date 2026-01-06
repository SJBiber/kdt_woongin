import os
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()
#
# YouTube API 설정
# 구글 클라우드 콘솔에서 발급받은 API 키를 .env 파일에 입력하세요.
API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

"""
YouTube에서 키워드를 검색하고 영상 목록과 상세 통계 데이터를 가져오는 함수입니다.
:param query: 검색할 키워드 (문자열)
:param max_results: 한 번에 가져올 검색 결과 개수 (최대 50개)
:return: 수집된 데이터가 담긴 Pandas DataFrame
"""
def youtube_search(query, max_results=50):
    if not API_KEY:
        print("에러: YOUTUBE_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return None

    # googleapiclient.discovery.build: YouTube 서비스 객체를 생성합니다.
    # 이 객체를 통해 YouTube API의 여러 기능을 호출할 수 있습니다.
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    # youtube.search().list: 유튜브의 'Search' 리소스를 호출하여 키워드 검색을 수행합니다.
    # - q: 검색어
    # - part: 가져올 정보의 종류 (id, snippet은 기본 정보 포함)
    # - order: 정렬 순서 (date는 최신순)
    # .execute(): 실제 API 요청을 보내고 결과를 받아옵니다.
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results,
        type='video',
        order='date'  # 최신순 정렬
    ).execute()

    videos = []
    video_ids = []

    for item in search_response.get('items', []):
        video_ids.append(item['id']['videoId'])
        videos.append({
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'published_at': item['snippet']['publishedAt'],
            'channel_title': item['snippet']['channelTitle']
        })

    # youtube.videos().list: 검색 결과로 얻은 영상 ID들의 상세 통계 정보를 가져옵니다.
    # (검색 API만으로는 조회수를 바로 알 수 없어서 이 단계를 거칩니다.)
    # - part: 'statistics'는 조회수, 좋아요 등의 통계를 포함합니다.
    # - id: 콤마(,)로 구분된 영상 ID 목록
    stats_response = youtube.videos().list(
        part='statistics',
        id=','.join(video_ids)
    ).execute()

    # 조회수 매핑
    stats_map = {item['id']: item['statistics'].get('viewCount', 0) for item in stats_response.get('items', [])}

    for video in videos:
        video['view_count'] = int(stats_map.get(video['video_id'], 0))

    return pd.DataFrame(videos)

"""
수집된 데이터를 Pandas를 활용해 일별로 분석하고 통계를 내는 함수입니다.
:param df: 수집된 영상 정보가 담긴 DataFrame
:return: 일별 분석 결과 리포트 (DataFrame)
"""
def analyze_data(df):
    if df is None or df.empty:
        print("분석할 데이터가 없습니다.")
        return

    # 날짜 형식 변환 (YYYY-MM-DD)
    df['published_at'] = pd.to_datetime(df['published_at']).dt.date

    # 일별 업로드 수 계산
    daily_uploads = df.groupby('published_at').size().reset_index(name='upload_count')
    
    # 일별 총 조회수 계산
    daily_views = df.groupby('published_at')['view_count'].sum().reset_index(name='total_views')

    # 결과 병합
    result = pd.merge(daily_uploads, daily_views, on='published_at')
    
    print("\n--- 일별 분석 결과 ---")
    print(result)
    
    print("\n--- 전체 요약 ---")
    print(f"총 영상 수: {len(df)}개")
    print(f"전체 누적 조회수: {df['view_count'].sum():,}회")
    
    return result

if __name__ == "__main__":
    keyword = input("검색할 키워드를 입력하세요: ")
    data = youtube_search(keyword)
    
    if data is not None:
        analyze_data(data)
        # CSV로 저장
        data.to_csv(f'youtube_{keyword}_results.csv', index=False, encoding='utf-8-sig')
        print(f"\n파일 저장 완료: youtube_{keyword}_results.csv")
