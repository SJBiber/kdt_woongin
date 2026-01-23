import os
from dotenv import load_dotenv

from pathlib import Path

# 설정 로드 - config/.env
config_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=config_path)

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Crawler Settings
    HEADLESS = False  # Set to True for production
    TIMEOUT = 30000

settings = Settings()
