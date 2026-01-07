import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class Settings:
    # YouTube API
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Analysis Thresholds
    VIRAL_THRESHOLD_POWER = 1000.0 # Power Score (Views per Hour) 기준
    SURGE_THRESHOLD_RATIO = 0.5   # 최근 24시간 내 업로드 비중 기준 (50%)
    
    # Scheduling & Limits (Quota Optimized)
    TREND_CHECK_INTERVAL = 120   # 주기를 2시간으로 완만하게 조정
    TOP_KEYWORDS_COUNT = 8       # 핵심 키워드 8개만 집중 분석
    SEARCH_MAX_RESULTS = 50      # API 1회 요청(100 unit)으로 끝내기 위해 50개로 제한
    STATS_CHECK_INTERVAL = 30

    # Notification
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

settings = Settings()
