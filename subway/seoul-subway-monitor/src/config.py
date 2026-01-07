import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Base URL for Seoul Wireless Realtime Position API
    # Format: http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimePosition/{START}/{END}/{SUBWAY_NAME}
    SEOUL_API_BASE_URL = "http://swopenAPI.seoul.go.kr/api/subway"

    @classmethod
    def validate(cls):
        if not cls.SEOUL_API_KEY:
            raise ValueError("SEOUL_API_KEY is not set in environment variables.")
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is not set in environment variables.")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is not set in environment variables.")
