-- YouTube 인기 동영상 Top 10 수집 테이블
CREATE TABLE IF NOT EXISTS youtube_top_10 (
    id BIGSERIAL PRIMARY KEY,
    rank INTEGER NOT NULL,            -- 1~10위 자료
    video_id TEXT NOT NULL,
    title TEXT,
    channel_title TEXT,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,        -- 댓글 수 추가
    keywords TEXT,                   -- 콤마(,)로 구분된 주요 키워드 리스트
    analysis_type TEXT,              -- 'TRENDING' 또는 'HISTORICAL' 구분
    uploaded_at TIMESTAMPTZ,         -- 영상 업로드 날짜 추가
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 조회 성능 향상을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_youtube_top10_date ON youtube_top_10(collected_at);
CREATE INDEX IF NOT EXISTS idx_youtube_top10_rank ON youtube_top_10(rank);
