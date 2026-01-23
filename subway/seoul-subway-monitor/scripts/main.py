import time
import schedule
import logging
import sys
import os
from datetime import datetime

from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT)) # src/ 에 접근 가능하게
sys.path.insert(0, str(PROJECT_ROOT / 'config')) # config/ 내 설정 모듈 접근 가능하게

from config import Config
from src.api_client import SeoulSubwayAPI
from src.db_client import SubwayDB

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# List of subway lines to monitor
# Note: Use exact names expected by the API. 
# Common names: '1호선', '2호선', '3호선', '4호선', '5호선', '6호선', '7호선', '8호선', '9호선', 
# '경의중앙선', '분당선', '공항철도', '신분당선' etc.
TARGET_LINES = [
    '1호선', '2호선', '3호선', '4호선', '5호선', 
    '6호선', '7호선', '8호선', '9호선'
]

def job():
    logger.info("Starting data collection job...")
    
    try:
        api = SeoulSubwayAPI()
        db = SubwayDB()
        
        total_collected = 0
        
        for line in TARGET_LINES:
            positions = api.get_realtime_positions(line)
            if positions:
                db.insert_positions(positions)
                total_collected += len(positions)
                logger.info(f"Collected {len(positions)} positions for {line}")
            else:
                logger.debug(f"No positions for {line}")
            
            # Rate limiting / politeness
            time.sleep(0.5)
            
        logger.info(f"Job completed. Total records inserted: {total_collected}")
        
    except Exception as e:
        logger.error(f"Job failed with error: {e}")
        sys.exit(1)

def main():
    logger.info("Initializing Seoul Subway Monitor...")
    
    # Run once at startup to verify
    job()
    
    # Schedule job every 1 minute (Realtime data updates frequently)
    schedule.every(1).minutes.do(job)
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")

if __name__ == "__main__":
    main()
