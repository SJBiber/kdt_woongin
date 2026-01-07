-- AI가 분석한 카테고리별 통합 트렌드 테이블
CREATE TABLE IF NOT EXISTS youtube_category_trends (
    id BIGSERIAL PRIMARY KEY,
    category_name TEXT NOT NULL,      -- 예: 게임, 영화, 음악, 사회/뉴스 등
    video_count INTEGER NOT NULL,     -- 해당 카테고리에 속한 영상 개수
    total_views BIGINT NOT NULL,      -- 해당 카테고리 영상들의 총 조회수 합산
    analysis_type TEXT NOT NULL,      -- TRENDING 또는 HISTORICAL
    representative_keywords TEXT,      -- 해당 카테고리를 대표하는 키워드들 (AI 추출)
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_cat_trend_type ON youtube_category_trends(analysis_type);
CREATE INDEX IF NOT EXISTS idx_cat_trend_date ON youtube_category_trends(analyzed_at);
