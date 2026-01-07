import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db_client import SubwayDB

def analyze_intervals(line_name: str = "3호선"):
    db = SubwayDB()
    
    # Fetch data for the last 1 hour
    # For now, let's just fetch recent 2000 records
    response = db.get_recent_positions(limit=5000, line_name=line_name)
    if not response:
        print(f"No data found for {line_name}")
        return
    
    df = pd.DataFrame(response)
    df['last_rec_time'] = pd.to_datetime(df['last_rec_time'])
    
    # We only care about arrivals (train_status=1) to measure intervals at a station
    # Or simplified: arrivals/entries/departures. Let's use status=1 as "arrival at station"
    arrivals = df[df['train_status'] == '1'].copy()
    
    if arrivals.empty:
        print("No arrival events (status 1) found for interval analysis.")
        return

    # Sort by station and time
    arrivals = arrivals.sort_values(['station_name', 'direction_type', 'last_rec_time'])
    
    # Calculate interval between consecutive trains at the same station and direction
    arrivals['prev_train_time'] = arrivals.groupby(['station_name', 'direction_type'])['last_rec_time'].shift(1)
    arrivals['prev_train_no'] = arrivals.groupby(['station_name', 'direction_type'])['train_number'].shift(1)
    
    # Interval in minutes
    arrivals['interval'] = (arrivals['last_rec_time'] - arrivals['prev_train_time']).dt.total_seconds() / 60.0
    
    # Filter out duplicate records for the same train arrival (API might return the same event multiple times)
    # We only want the first time a train arrived at that station in this window
    arrivals = arrivals.drop_duplicates(subset=['station_name', 'direction_type', 'train_number'], keep='first')
    
    # Recalculate interval after dropping duplicates
    arrivals['prev_train_time'] = arrivals.groupby(['station_name', 'direction_type'])['last_rec_time'].shift(1)
    arrivals['interval'] = (arrivals['last_rec_time'] - arrivals['prev_train_time']).dt.total_seconds() / 60.0

    # Summary
    print(f"\n=== Interval Analysis for {line_name} ===")
    stats = arrivals['interval'].dropna().describe()
    print(stats)
    
    # Identify bottleneck stations (long intervals)
    long_intervals = arrivals[arrivals['interval'] > 10].sort_values('interval', ascending=False)
    if not long_intervals.empty:
        print("\n--- Significant Gaps (> 10 min) ---")
        print(long_intervals[['last_rec_time', 'station_name', 'direction_type', 'train_number', 'interval']].head(10))

    # Identify bunching (short intervals)
    bunching = arrivals[arrivals['interval'] < 1.5].sort_values('interval')
    if not bunching.empty:
        print("\n--- Train Bunching (< 1.5 min) ---")
        print(bunching[['last_rec_time', 'station_name', 'direction_type', 'train_number', 'interval']].head(10))

if __name__ == "__main__":
    # You can change the line name as needed
    analyze_intervals("3호선")
