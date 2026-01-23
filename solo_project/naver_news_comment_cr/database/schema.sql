-- 네이버 뉴스 댓글 테이블 생성
-- Opinion_Analysis 프로젝트와 호환되는 구조

DROP TABLE IF EXISTS naver_news_comments;

CREATE TABLE naver_news_comments (
    comment_id TEXT PRIMARY KEY,        -- 댓글 고유 ID
    news_id TEXT NOT NULL,              -- 뉴스 기사 ID (기존 video_id 대응)
    author TEXT,                        -- 작성자
    content TEXT,                       -- 댓글 내용
    likes INTEGER DEFAULT 0,            -- 공감 수
    dislikes INTEGER DEFAULT 0,         -- 비공감 수
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

-- 빠른 조회를 위한 인덱스 생성
CREATE INDEX idx_news_id ON naver_news_comments(news_id);
CREATE INDEX idx_sentiment_label ON naver_news_comments(sentiment_label);
CREATE INDEX idx_llm_sentiment ON naver_news_comments(llm_sentiment);
CREATE INDEX idx_published_at ON naver_news_comments(published_at);
