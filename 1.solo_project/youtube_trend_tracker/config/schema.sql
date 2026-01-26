-- ========================================
-- YouTube 일별 영상 트렌드 추적 테이블
-- ========================================
-- 목적: 특정 날짜에 업로드된 영상들의 통계를 매일 재조회하여 증가 추이 분석
-- 사용법: Supabase SQL Editor에서 실행

CREATE TABLE daily_video_trends (
    -- 기본 정보
    keyword TEXT NOT NULL,              -- 검색 키워드 (예: "임성근 쉐프")
    upload_date DATE NOT NULL,          -- 영상이 업로드된 날짜
    collected_date DATE NOT NULL,       -- 데이터를 수집한 날짜
    
    -- 통계 데이터
    video_count INT DEFAULT 0,          -- 해당 날짜에 업로드된 영상 개수
    total_views BIGINT DEFAULT 0,       -- 총 조회수
    total_likes BIGINT DEFAULT 0,       -- 총 좋아요
    total_comments BIGINT DEFAULT 0,    -- 총 댓글
    
    -- 증가량 (전날 대비)
    views_growth BIGINT DEFAULT 0,      -- 조회수 증가량
    likes_growth BIGINT DEFAULT 0,      -- 좋아요 증가량
    comments_growth BIGINT DEFAULT 0,   -- 댓글 증가량
    
    -- 증가율 (%)
    views_growth_rate DECIMAL(10, 2) DEFAULT 0,     -- 조회수 증가율
    likes_growth_rate DECIMAL(10, 2) DEFAULT 0,     -- 좋아요 증가율
    comments_growth_rate DECIMAL(10, 2) DEFAULT 0,  -- 댓글 증가율
    
    -- 메타 정보
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    
    -- 기본 키: 키워드 + 업로드 날짜 + 수집 날짜 조합으로 유일성 보장
    PRIMARY KEY (keyword, upload_date, collected_date)
);

-- ========================================
-- 인덱스 생성 (검색 속도 향상)
-- ========================================

-- 키워드 + 수집 날짜로 검색 (대시보드에서 최신 데이터 조회 시)
CREATE INDEX idx_keyword_collected 
ON daily_video_trends(keyword, collected_date DESC);

-- 업로드 날짜로 검색 (특정 날짜 영상의 추이 분석 시)
CREATE INDEX idx_upload_date 
ON daily_video_trends(upload_date DESC);

-- 키워드 + 업로드 날짜로 검색 (시계열 분석 시)
CREATE INDEX idx_keyword_upload 
ON daily_video_trends(keyword, upload_date DESC);

-- ========================================
-- 자동 업데이트 트리거 (updated_at 자동 갱신)
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_daily_video_trends_updated_at 
BEFORE UPDATE ON daily_video_trends
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 샘플 쿼리 (참고용)
-- ========================================

-- 1. 최신 수집 데이터 조회
-- SELECT * FROM daily_video_trends 
-- WHERE keyword = '임성근 쉐프' 
-- AND collected_date = CURRENT_DATE 
-- ORDER BY upload_date DESC;

-- 2. 특정 업로드 날짜의 추이 조회
-- SELECT upload_date, collected_date, total_views, views_growth 
-- FROM daily_video_trends 
-- WHERE keyword = '임성근 쉐프' 
-- AND upload_date = '2026-01-15'
-- ORDER BY collected_date;

-- 3. 관심도 하락 분석 (증가율이 낮은 날짜)
-- SELECT upload_date, collected_date, views_growth_rate
-- FROM daily_video_trends 
-- WHERE keyword = '임성근 쉐프' 
-- AND collected_date = CURRENT_DATE
-- ORDER BY views_growth_rate ASC
-- LIMIT 10;
