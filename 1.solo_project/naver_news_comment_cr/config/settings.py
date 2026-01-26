"""
환경 설정 관리 모듈
.env 파일에서 환경 변수를 로드하고 관리함
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 찾기
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / "config" / ".env"

# .env 파일 로드
load_dotenv(ENV_PATH)

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 네이버 API 설정 (선택사항)
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 크롤링 설정
MAX_NEWS_COUNT = int(os.getenv("MAX_NEWS_COUNT", 10))
MAX_COMMENTS_PER_NEWS = int(os.getenv("MAX_COMMENTS_PER_NEWS", 100))

# 필수 환경 변수 검증
def validate_config():
    """필수 환경 변수가 설정되었는지 확인"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase 설정이 필요합니다. "
            "config/.env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정하세요."
        )
    print("✅ 환경 설정 검증 완료")

if __name__ == "__main__":
    validate_config()
