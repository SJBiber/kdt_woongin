import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

class YouTubeReviewAnalyzer:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # 분석용 사전 (블로그 분석기와 유사하게 구성 가능)
        self.lexicon = {
            "positive": ["맛있다", "최고", "대박", "신기", "기대", "성공", "좋아요", "사고싶다"],
            "negative": ["비싸다", "사악", "질림", "거품", "탕후루꼴", "돈아깝", "별로", "실패"],
            "interest": ["안올라오나", "최근", "소식", "어디"]
        }

    def fetch_comments(self, video_ids=None):
        """Supabase에서 댓글 데이터 로드"""
        query = self.supabase.table("youtube_comments").select("*")
        if video_ids:
            query = query.in_("video_id", video_ids)
        
        response = query.execute()
        return response.data

    def analyze_decay_rate(self, video_id, published_at):
        """관심도 감쇠 지표(Decay Rate) 계산
        - 과거 영상에 '최근' 댓글이 얼마나 달리는가 확인
        """
        # 해당 영상의 모든 댓글 로드
        comments = self.supabase.table("youtube_comments")\
            .select("published_at")\
            .eq("video_id", video_id)\
            .execute().data
        
        if not comments:
            return 0.0
        
        df = pd.DataFrame(comments)
        df['published_at'] = pd.to_datetime(df['published_at'])
        
        # 최근 7일 내 댓글 수
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_count = len(df[df['published_at'] >= seven_days_ago])
        total_count = len(df)
        
        # 감쇠율 (최근 댓글 비중)
        decay_rate = (recent_count / total_count) * 100 if total_count > 0 else 0
        return decay_rate

    def analyze_sentiment(self, text):
        """댓글 텍스트 감성 키워드 분석"""
        pos_hits = sum(1 for k in self.lexicon["positive"] if k in text)
        neg_hits = sum(1 for k in self.lexicon["negative"] if k in text)
        
        if pos_hits > neg_hits:
            return "긍정"
        elif neg_hits > pos_hits:
            return "부정"
        return "중립"

    def run_temporal_analysis(self):
        """시계열 여론 변화 분석 실행 보고서 생성"""
        comments = self.fetch_comments()
        if not comments:
            print("데이터가 없습니다.")
            return

        df = pd.DataFrame(comments)
        df['published_at'] = pd.to_datetime(df['published_at'])
        
        # 기간별 분리 (도입기 vs 성숙기)
        # 예: 25년 11월 이전 vs 26년 1월 이후
        intro_period = df[df['published_at'] < '2025-12-01']
        current_period = df[df['published_at'] >= '2026-01-01']
        
        print("=== 유튜브 시계열 여론 분석 (도입기 vs 현재) ===")
        
        for name, data in [("도입기 (25년 11월 이전)", intro_period), ("성숙기 (26년 1월 이후)", current_period)]:
            print(f"\n[{name}]")
            if data.empty:
                print("  데이터 없음")
                continue
            
            sentiments = data['text'].apply(self.analyze_sentiment)
            sentiment_counts = sentiments.value_counts(normalize=True) * 100
            
            print(f"  - 수집 댓글 수: {len(data)}")
            for label, pct in sentiment_counts.items():
                print(f"  - {label} 비율: {pct:.1f}%")

if __name__ == "__main__":
    analyzer = YouTubeReviewAnalyzer()
    analyzer.run_temporal_analysis()
