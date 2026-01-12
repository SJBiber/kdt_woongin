import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Crawler Settings
    HEADLESS = False  # Set to True for production
    TIMEOUT = 30000

settings = Settings()
