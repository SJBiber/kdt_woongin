import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class StatAnalyzer:
    def __init__(self, df):
        """
        :param df: 분석할 데이터프레임 (Supabase에서 읽어온 데이터)
        """
        self.df = df
        if not self.df.empty:
            self.df['published_at'] = pd.to_datetime(self.df['published_at'])
            
            # 6종 감정 라벨(정수)을 통계 수치로 변환
            # 0:support(+1), 1:anger(-1), 2:neutral(0), 3:disappointment(-0.5), 4:sarcasm(-0.8), 5:inquiry(0)
            sentiment_map = {
                0: 1.0,   # support
                1: -1.0,  # anger
                2: 0.0,   # neutral
                3: -0.5,  # disappointment
                4: -0.8,  # sarcasm
                5: 0.0    # inquiry
            }
            self.df['sentiment_val'] = self.df['sentiment_label'].map(sentiment_map).fillna(0)

    def get_correlation(self):
        """좋아요 수와 감성 점수의 상관관계 분석"""
        if self.df.empty:
            return None
            
        corr, p_value = stats.pearsonr(self.df['likes'], self.df['sentiment_score'])
        return {
            "correlation": corr,
            "p_value": p_value,
            "interpretation": "Significant" if p_value < 0.05 else "Not Significant"
        }

    def time_series_resilience(self):
        """시간에 따른 감성 변화 (회복 탄력성 기초 분석)"""
        if self.df.empty:
            return None
            
        # 일별 감성 평균값
        daily_sentiment = self.df.set_index('published_at').resample('D')['sentiment_val'].mean()
        return daily_sentiment

    def polarization_index(self):
        """여론 극단화 지수 (감성 점수의 표준편차 활용)"""
        if self.df.empty:
            return 0
        return self.df['sentiment_score'].std()

if __name__ == "__main__":
    # 가상 데이터 테스트
    data = {
        'likes': [10, 5, 100, 2, 50],
        'sentiment_score': [0.9, 0.2, 0.95, 0.1, 0.8],
        'sentiment_label': [0, 1, 0, 3, 4], # support, anger, support, disappointment, sarcasm
        'published_at': ['2026-01-01', '2026-01-02', '2026-01-15', '2026-01-20', '2026-01-21']
    }
    test_df = pd.DataFrame(data)
    analyzer = StatAnalyzer(test_df)
    print(f"Correlation Analysis: {analyzer.get_correlation()}")
    print(f"Polarization Index: {analyzer.polarization_index()}")
