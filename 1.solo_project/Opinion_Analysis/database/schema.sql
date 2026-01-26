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
    -- 0: support (고마움(비꼬는것이 아닌 순수한 고마움), 도움된다, 사랑, 지지, 응원, 복귀 기대("언제와요", "보고싶다"), 사과 수용, 위로, "정치인보다 이분이다" 식의 방어/옹호)
    -- 1: anger (분노, 욕설, 공격적 비판, 나락, 전과자 언급 등 강한 적대감)
    -- 2: neutral (중립, 감정 없는 짧은 인사, 무의미한 나열, 주제를 벗어난 과도한 정치 댓글)
    -- 3: disappointment (실망, 유감, "믿었는데 아쉽다", 팬이었으나 돌아섬, 구독취소 언급)
    -- 4: sarcasm (조롱, 비꼼, 반어법, 밈(Meme) 사용, 비꼬는 의도의 이모티콘('^^', 'ㅋㅋ' 등 문맥상 조롱 , 칭찬하는척하면서 비꼬는글))
    -- 5: inquiry (질문, 정보 요청, 상황 파악, 또는 유튜버가 아닌 '작성자들끼리 싸우는 댓글')

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