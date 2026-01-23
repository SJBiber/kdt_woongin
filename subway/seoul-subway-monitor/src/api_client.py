import requests
import logging
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# 프로젝트 루트 경로 설정 (config/ 에 접근하기 위함)
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / 'config') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'config'))

from config import Config

logger = logging.getLogger(__name__)

class SeoulSubwayAPI:
    def __init__(self):
        Config.validate()
        self.api_key = Config.SEOUL_API_KEY
        self.base_url = Config.SEOUL_API_BASE_URL

    def get_realtime_positions(self, line_name: str) -> List[Dict[str, Any]]:
        """
        Fetch real-time train positions for a specific subway line.
        
        Args:
            line_name (str): The name of the subway line (e.g., '1호선', '2호선', '신분당선').
                             Important: The API expects specific names.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing train position data.
            Returns empty list if error occurs or no data.
        """
        # Encode line_name for URL ? Actually requests handles it but usually this API path param needs to be raw string if using path based
        # The document says: /api/subway/{KEY}/json/realtimePosition/{START}/{END}/{subwayNm}
        
        # We need to request a sufficient range. 0 to 100 should cover most trains on a line at once? 
        # Actually usually there are many trains. Let's try 0 to 500 to be safe.
        start_index = 0
        end_index = 300 
        
        url = f"{self.base_url}/{self.api_key}/json/realtimePosition/{start_index}/{end_index}/{line_name}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if 'realtimePositionList' in data:
                return data['realtimePositionList']
            elif 'RESULT' in data and 'CODE' in data['RESULT']:
                code = data['RESULT']['CODE']
                if code == 'INFO-000':
                    # No data found (normal if no trains run directly matching query or wrong line name)
                    logger.info(f"No realtime position data found for {line_name} (INFO-000)")
                    return []
                else:
                    logger.error(f"API Error for {line_name}: {data['RESULT']['MESSAGE']} ({code})")
                    return []
            else:
                logger.warning(f"Unexpected API response structure for {line_name}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching data for {line_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching data for {line_name}: {e}")
            return []
