-- 1. 전역 트렌드 스냅샷 (인기 급상승 리스트 원본 보관)
CREATE TABLE IF NOT EXISTS trending_snapshots (
    id BIGSERIAL PRIMARY KEY,
    video_id TEXT NOT NULL,
    title TEXT,
    channel_title TEXT,
    rank INTEGER,                  -- 1~300위 순위
    view_count BIGINT,
    like_count BIGINT,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 키워드별 분석 결과 (Snapshot Analysis 핵심 테이블)
CREATE TABLE IF NOT EXISTS trend_analysis (
    id BIGSERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    topic_share FLOAT,             -- 인기 급상승 내 비중 (%)
    power_score FLOAT,             -- 시간당 평균 조회수 상승폭
    recent_ratio FLOAT,            -- 24시간 내 업로드 신선도 비중 (0~1)
    avg_views FLOAT,               -- 평균 조회수 추가
    total_vols INTEGER,            -- 수집된 업로드 개수 추가
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 바이럴 알림 로그
CREATE TABLE IF NOT EXISTS viral_alerts (
    id BIGSERIAL PRIMARY KEY,
    keyword TEXT,
    alert_type TEXT,               -- 'SURGE' (공급폭발), 'POWER' (조회수폭발)
    score_value FLOAT,
    description TEXT,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 설정 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_analysis_keyword ON trend_analysis(keyword);
CREATE INDEX IF NOT EXISTS idx_analysis_time ON trend_analysis(collected_at);
