import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.db_client import SubwayDB

def analyze_dwell_time(line_name: str = "3호선"):
    db = SubwayDB()
    response = db.get_recent_positions(limit=5000, line_name=line_name)
    if not response:
        print(f"No data found for {line_name}")
        return
    
    df = pd.DataFrame(response)
    df['last_rec_time'] = pd.to_datetime(df['last_rec_time'])
    
    # Sort by train, station, and time
    df = df.sort_values(['train_number', 'station_name', 'last_rec_time'])
    
    # We want to find pairs of (status=1) and (status=2) for the same train at the same station
    # status 1: Arrival, 2: Departure
    
    results = []
    
    for (train_no, station_name), group in df.groupby(['train_number', 'station_name']):
        arrival = group[group['train_status'] == '1'].sort_values('last_rec_time').head(1)
        departure = group[group['train_status'] == '2'].sort_values('last_rec_time').head(1)
        
        if not arrival.empty and not departure.empty:
            arr_time = arrival['last_rec_time'].iloc[0]
            dep_time = departure['last_rec_time'].iloc[0]
            
            if dep_time > arr_time:
                dwell_time = (dep_time - arr_time).total_seconds()
                results.append({
                    'train_number': train_no,
                    'station_name': station_name,
                    'arrival_time': arr_time,
                    'departure_time': dep_time,
                    'dwell_time_sec': dwell_time
                })
    
    if not results:
        print("No dwell time samples found (need status 1 followed by status 2).")
        return
        
    dwell_df = pd.DataFrame(results)
    
    print(f"\n=== Dwell Time Analysis for {line_name} ===")
    print(dwell_df['dwell_time_sec'].describe())
    
    # Hotspots: Stations with high average dwell time
    hotspots = dwell_df.groupby('station_name')['dwell_time_sec'].agg(['mean', 'count', 'max']).sort_values('mean', ascending=False)
    print("\n--- Delay Hotspots (Average Dwell Time) ---")
    print(hotspots.head(10))
    
    # Outliers: Individual trains stuck at a station
    outliers = dwell_df[dwell_df['dwell_time_sec'] > 120].sort_values('dwell_time_sec', ascending=False)
    if not outliers.empty:
        print("\n--- Individual Delays (> 2 min) ---")
        print(outliers[['train_number', 'station_name', 'dwell_time_sec']].head(10))

if __name__ == "__main__":
    analyze_dwell_time("3호선")
