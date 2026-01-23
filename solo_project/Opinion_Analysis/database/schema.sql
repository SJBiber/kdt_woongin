-- 1. 기존 테이블 삭제 (데이터가 모두 날아가니 주의하세요!)
DROP TABLE IF EXISTS im_sung_gen_youtube_comments;
-- 2. 정수형 기반 최적화 테이블 생성
CREATE TABLE im_sung_gen_youtube_comments (
    comment_id TEXT PRIMARY KEY,        -- 유튜브 댓글 고유 ID
    video_id TEXT NOT NULL,             -- 비디오 ID
    author TEXT,                        -- 작성자
    content TEXT,                       -- 댓글 내용
    likes INTEGER DEFAULT 0,            -- 좋아요 수
    published_at TIMESTAMP WITH TIME ZONE, -- 작성 시간
    
    -- 분석 필드 (정수형 최적화)
    -- 0: positive(긍정/응원)
    -- 1: negative(부정/조롱/비판)
    -- 2: neutral(중립/질문)
    sentiment_label INTEGER,            -- BERT 분석 결과
    sentiment_score FLOAT,              -- BERT 확신도 (0~1)
    llm_sentiment INTEGER,              -- DeepSeek 분석 결과
    
    keywords TEXT[],                    -- 추출된 키워드 리스트 (워드클라우드용)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 3. 빠른 조회를 위한 인덱스 생성
CREATE INDEX idx_sentiment_label ON im_sung_gen_youtube_comments(sentiment_label);
CREATE INDEX idx_llm_sentiment ON im_sung_gen_youtube_comments(llm_sentiment);
CREATE INDEX idx_published_at ON im_sung_gen_youtube_comments(published_at);