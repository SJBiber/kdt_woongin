-- 백종원 유튜브 댓글 테이블 생성
-- 임성근 테이블과 동일한 구조 사용 (6가지 감정 카테고리 0-5)

CREATE TABLE IF NOT EXISTS baek_jongwon_youtube_comments (
    comment_id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    video_title TEXT,
    video_upload_date DATE,
    content TEXT NOT NULL,
    author TEXT,
    likes INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    
    -- 분석 결과 (임성근과 동일한 구조)
    keywords TEXT[],
    sentiment_label TEXT,  -- BERT 분석 결과 (긍정/부정/중립)
    sentiment_score FLOAT, -- BERT 신뢰도 점수
    llm_sentiment INTEGER, -- DeepSeek LLM 분석 (0-5, 임성근과 동일한 6가지 카테고리)
    
    -- 메타데이터
    collection_period TEXT, -- 'controversy' (논란시기 2025.02-03) or 'current' (현재 2025.12-2026.01)
    target_person TEXT DEFAULT '백종원',
    collected_date DATE DEFAULT CURRENT_DATE,
    
    UNIQUE(comment_id, video_id)
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_baek_video_id ON baek_jongwon_youtube_comments(video_id);
CREATE INDEX IF NOT EXISTS idx_baek_published_at ON baek_jongwon_youtube_comments(published_at);
CREATE INDEX IF NOT EXISTS idx_baek_collection_period ON baek_jongwon_youtube_comments(collection_period);
CREATE INDEX IF NOT EXISTS idx_baek_sentiment_label ON baek_jongwon_youtube_comments(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_baek_llm_sentiment ON baek_jongwon_youtube_comments(llm_sentiment);

-- 코멘트
COMMENT ON TABLE baek_jongwon_youtube_comments IS '백종원 관련 유튜브 댓글 데이터 (논란 시기 vs 현재 비교 분석용)';
COMMENT ON COLUMN baek_jongwon_youtube_comments.collection_period IS '수집 시기: controversy (2025.02-03 논란시기) / current (2025.12-2026.01 현재)';
COMMENT ON COLUMN baek_jongwon_youtube_comments.llm_sentiment IS 'DeepSeek LLM 감정 분석 (임성근과 동일): 0(support), 1(anger), 2(neutral), 3(disappointment), 4(sarcasm), 5(inquiry)';
