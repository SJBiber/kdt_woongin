import logging
from typing import List, Dict, Any
from supabase import create_client, Client
import sys
from pathlib import Path

# 프로젝트 루트 경로 설정 (config/ 에 접근하기 위함)
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / 'config') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'config'))

from config import Config

logger = logging.getLogger(__name__)

class SubwayDB:
    def __init__(self):
        Config.validate()
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = "realtime_subway_positions"

    def insert_positions(self, positions_data: List[Dict[str, Any]]) -> None:
        """
        Transform and insert subway position data into Supabase.
        
        Args:
            positions_data (List[Dict[str, Any]]): List of raw data dictionaries from API.
        """
        if not positions_data:
            return

        formatted_data = [self._transform_data(item) for item in positions_data]
        
        try:
            # Supabase insert
            response = self.supabase.table(self.table_name).insert(formatted_data).execute()
            # Note: supabase-py v2 returns an object with .data, .count - check if successful if needed.
            # But usually raise exception on failure? 
            # Actually postgrest-py (underlying) might not raise for all errors, but `execute()` does perform the request.
            
            logger.info(f"Successfully inserted {len(formatted_data)} records.")
            
        except Exception as e:
            logger.error(f"Failed to insert data into Supabase: {e}")

    def get_recent_positions(self, limit: int = 1000, line_name: str = None) -> List[Dict[str, Any]]:
        """
        Fetch recent subway positions for analysis.
        """
        try:
            query = self.supabase.table(self.table_name).select("*").order("last_rec_time", desc=True).limit(limit)
            
            if line_name:
                query = query.eq("line_name", line_name)
                
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch data from Supabase: {e}")
            return []

    def _transform_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map API columns to Database columns.
        """
        # Mapping based on AGENT.md
        return {
            'line_id': raw_data.get('subwayId'),
            'line_name': raw_data.get('subwayNm'),
            'station_id': raw_data.get('statnId'),
            'station_name': raw_data.get('statnNm'),
            'train_number': raw_data.get('trainNo'),
            'last_rec_date': raw_data.get('lastRecptnDt'),
            'last_rec_time': raw_data.get('recptnDt'),
            'direction_type': raw_data.get('updnLine'),
            'dest_station_id': raw_data.get('statnTid'),
            'dest_station_name': raw_data.get('statnTnm'),
            'train_status': raw_data.get('trainSttus'),
            'is_express': raw_data.get('directAt'),
            'is_last_train': raw_data.get('lstcarAt') == '1'  # Convert '0'/'1' string to boolean
        }
