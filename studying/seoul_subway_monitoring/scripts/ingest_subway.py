import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

from pathlib import Path

# 설정 로드 - config/.env
config_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=config_path)

# Configuration
SEOUL_API_KEY = os.getenv("SEOUL_DATA_API_KEY", "sample")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate Configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file.")
    exit(1)

# API Endpoint Configuration
# Format: http://swopenapi.seoul.go.kr/api/subway/{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/{statnNm}
BASE_URL = "http://swopenapi.seoul.go.kr/api/subway"
SERVICE = "realtimePosition"
TYPE = "json" # Using JSON for easier parsing

# List of all supported subway lines
ALL_LINES = [
    "1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선", "9호선",
    "경의중앙선", "공항철도", "경춘선", "수인분당선", "신분당선", "우이신설선", "GTX-A", "신림선"
]

def fetch_realtime_data(subway_line_name, start_index=0, end_index=100):
    """
    Fetches real-time subway position data from Seoul Open Data API.
    """
    # URL Encoding is handled by requests, but for the path string construction:
    # We construct the URL manually because the API path structure is specific.
    url = f"{BASE_URL}/{SEOUL_API_KEY}/{TYPE}/{SERVICE}/{start_index}/{end_index}/{subway_line_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "realtimePositionList" in data:
            return data["realtimePositionList"]
        elif "RESULT" in data:
             print(f"API Error/Info: {data['RESULT'].get('CODE', 'Unknown')} - {data['RESULT'].get('MESSAGE', 'No message')}")
             return []
        else:
            print("Unexpected API response structure.")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching data: {e}")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return []

def transform_data(raw_data_list):
    """
    Transforms raw API data to match Supabase schema.
    """
    transformed_list = []
    
    for item in raw_data_list:
        # Mapping based on implementation plan
        record = {
            "subway_id": item.get("subwayId"),
            "subway_name": item.get("subwayNm"),
            "station_id": item.get("statnId"),
            "station_name": item.get("statnNm"),
            "train_number": item.get("trainNo"),
            "last_reception_date": item.get("lastRecptnDt"),
            "reception_time": item.get("recptnDt"), 
            "up_down_line": int(item.get("updnLine")) if item.get("updnLine") is not None else None,
            "terminal_station_id": item.get("statnTid"),
            "terminal_station_name": item.get("statnTnm"),
            "train_status": int(item.get("trainSttus")) if item.get("trainSttus") is not None else None,
            "express_type": int(item.get("directAt")) if item.get("directAt") is not None else None,
            "is_last_train": int(item.get("lstcarAt")) if item.get("lstcarAt") is not None else None,
            # created_at is handled by DB default usually, but we can send if needed. Let DB handle it.
        }
        transformed_list.append(record)
        
    return transformed_list

def ingest_to_supabase(data):
    """
    Inserts data into 'realtime_subway_positions' table.
    """
    if not data:
        print("No data to ingest.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        response = supabase.table("realtime_subway_positions").insert(data).execute()
        # response is the APIResponse object
        # If successfully inserted, response.data will contain the inserted rows
        print(f"Successfully inserted {len(data)} records.")
    except Exception as e:
        print(f"Error inserting into Supabase: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seoul Subway Data Ingestion")
    parser.add_argument("--line", type=str, default="1호선", help="Subway line name (e.g., 1호선, 2호선)")
    parser.add_argument("--line-all", action="store_true", help="Fetch data for ALL subway lines")
    parser.add_argument("--loop", action="store_true", help="Run continuously every 60 seconds")
    parser.add_argument("--test-api", action="store_true", help="Only test API fetch and print output")
    parser.add_argument("--test-db", action="store_true", help="Insert a dummy record to DB")

    args = parser.parse_args()

    if args.test_db:
        print("Testing DB connection with dummy data...")
        dummy_data = [{
            "subway_id": "9999",
            "subway_name": "TestLine",
            "station_name": "TestStation",
            "train_number": "TEST001",
            "reception_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "up_down_line": 0,
            "train_status": 0
        }]
        ingest_to_supabase(dummy_data)
        exit()

        ingest_to_supabase(dummy_data)
        exit()

    # Determine target lines
    target_lines = ALL_LINES if args.line_all else [args.line]

    if args.loop:
        print(f"Starting loop for lines: {target_lines}...")
        while True:
            for line in target_lines:
                print(f"[{datetime.now()}] Fetching data for {line}...")
                
                # Sample key check (limit 5)
                range_end = 5 if SEOUL_API_KEY == "sample" else 100
                
                raw_data = fetch_realtime_data(line, 0, range_end)
                if args.test_api:
                    print(f"Fetched {len(raw_data)} records for {line}.")
                    if len(raw_data) > 0:
                        print("Sample:", raw_data[0])
                else:
                    cleaned_data = transform_data(raw_data)
                    ingest_to_supabase(cleaned_data)
                
                # Small sleep between API calls to be polite if fetching many
                time.sleep(1) 
            
            print("Waiting 60 seconds...")
            time.sleep(60) # Wait 60 seconds
    else:
        for line in target_lines:
            print(f"Fetching data for {line} once...")
            # Sample key allows max 5 records (1~5 or 0~4 depending on accounting, error message said 1~5)
            # Let's try 0 to 5.
            range_end = 5 if SEOUL_API_KEY == "sample" else 100
            raw_data = fetch_realtime_data(line, 0, range_end)
            if args.test_api:
                 print(json.dumps(raw_data, indent=2, ensure_ascii=False))
            else:
                cleaned_data = transform_data(raw_data)
                ingest_to_supabase(cleaned_data)
