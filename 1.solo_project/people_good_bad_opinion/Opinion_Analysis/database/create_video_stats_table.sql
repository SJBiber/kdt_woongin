-- YouTube 영상 통계 테이블 생성
CREATE TABLE IF NOT EXISTS im_sung_gen_video_stats (
    video_id VARCHAR(50) PRIMARY KEY,
    url TEXT,
    title TEXT,
    description TEXT,
    channel VARCHAR(255),
    upload_date DATE,
    is_before_controversy BOOLEAN,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    duration_sec INTEGER,
    engagement_rate DOUBLE PRECISION,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_video_stats_upload_date ON video_stats(upload_date);
CREATE INDEX IF NOT EXISTS idx_video_stats_is_before_controversy ON video_stats(is_before_controversy);
