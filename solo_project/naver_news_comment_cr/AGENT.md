## 프로젝트 개요

### 프로젝트 목표
네이버 뉴스 댓글 크롤링을 위한 프로젝트

### 프로젝트 기능
- 연관 키워드를 입력하여 관련 네이버 뉴스 댓글 크롤링
- 크롤링된 댓글을 DB에 저장
- 크롤링된 댓글을 분석하여 키워드를 추출
- 키워드를 기반으로 댓글을 분석하여 댓글의 감정을 분석

### 프로젝트 기술 스택
- Python (3.12)
- 정적 크롤링을 선호 하지만 불가능 하다면 동적 크롤링을 사용하도록 요청
- supabase

### 참고사항
- 소스생성 및 파일 생성시 각 역할의 디렉토리에 생성 부탁
- db 테이블은 하나 새로 만들고 진행 , 
    - 다음과 같은 필드를 함께 생성 부탁 , 이후 Opinion_Analysis 프로젝트에서 사용한 필드랑 같이 데이터로 쓸거라 동일하게 맞춤 부탁
    Opinion_Analysis 프로젝트의 테이블
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
