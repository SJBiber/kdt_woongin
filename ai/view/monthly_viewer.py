import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import re

# Mac 환경에서 한글 폰트 설정 (AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def visualize_monthly_stats(file_path):
    """
    CSV 파일을 읽어 월별 업로드 수와 총 조회수를 가로로 나란히 시각화합니다.
    """
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 날짜 컬럼을 datetime 객체로 변환
    df['published_at'] = pd.to_datetime(df['published_at'])
    
    # 월별(Year-Month) 컬럼 생성
    df['month'] = df['published_at'].dt.to_period('M').astype(str)
    
    # 월별 그룹화: 업로드 수(count)와 조회수(sum) 계산
    monthly_stats = df.groupby('month').agg(
        upload_count=('video_id', 'count'),
        total_views=('view_count', 'sum')
    ).reset_index()
    
    # 파일명에서 키워드 추출 (예: youtube_탄산마그네슘_results -> 탄산마그네슘)
    filename = os.path.basename(file_path)
    keyword = re.sub(r'youtube_(.*)_results\.csv', r'\1', filename)

    # 그래프 생성 (1행 2열)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. 월별 업로드 수 바 차트
    bars1 = ax1.bar(monthly_stats['month'], monthly_stats['upload_count'], color='skyblue', edgecolor='navy')
    ax1.set_title(f"[{keyword}] 월별 영상 업로드 수", fontsize=15, pad=20, fontweight='bold')
    ax1.set_xlabel("년-월", fontsize=11)
    ax1.set_ylabel("업로드 수 (개)", fontsize=11)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.tick_params(axis='x', labelrotation=45) # X축 라벨 회전시켜 겹침 방지
    
    # 막대 위에 숫자 표시
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9)

    # 2. 월별 총 조회수 바 차트
    bars2 = ax2.bar(monthly_stats['month'], monthly_stats['total_views'], color='salmon', edgecolor='darkred')
    ax2.set_title(f"[{keyword}] 월별 총 조회수", fontsize=15, pad=20, fontweight='bold')
    ax2.set_xlabel("년-월", fontsize=11)
    ax2.set_ylabel("총 조회수 (회)", fontsize=11)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.tick_params(axis='x', labelrotation=45) # X축 라벨 회전시켜 겹침 방지
    
    # Y축 숫자에 콤마 추가
    ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # 막대 위에 숫자 표시 (가독성을 위해 백만/천 단위로 표시)
    def format_view(n):
        if n >= 1_000_000: return f'{n/1_000_000:.1f}M'
        if n >= 1_000: return f'{n/1_000:.1f}K'
        return str(int(n))

    max_views = monthly_stats['total_views'].max()
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (max_views * 0.01),
                 format_view(height), ha='center', va='bottom', fontsize=9)

    # 레이아웃 조정 (제목과 그래프 겹침 방지)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.suptitle(f"유튜브 분석 결과 - 키워드: {keyword}", fontsize=18, fontweight='bold')
    
    print(f"--- {keyword} 월별 요약 ---")
    print(monthly_stats)
    
    plt.show()

if __name__ == "__main__":
    # 요청하신 파일 경로
    csv_path = "/Users/baeseungjae/Documents/GitHub/kdt_woongin/ai/api/youtube_임성근_results.csv"
    visualize_monthly_stats(csv_path)
