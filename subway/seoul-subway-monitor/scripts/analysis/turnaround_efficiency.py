import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.db_client import SubwayDB

def analyze_turnaround(line_name: str = "3호선"):
    db = SubwayDB()
    # Need more data for turnaround as it takes time
    response = db.get_recent_positions(limit=8000, line_name=line_name)
    if not response:
        print(f"No data found for {line_name}")
        return
    
    df = pd.DataFrame(response)
    df['last_rec_time'] = pd.to_datetime(df['last_rec_time'])
    
    # Sort by train and time
    df = df.sort_values(['train_number', 'last_rec_time'])
    
    turnarounds = []
    
    for train_no, group in df.groupby('train_number'):
        # Sort group by time
        group = group.sort_values('last_rec_time')
        
        # Look for direction changes
        group['prev_direction'] = group['direction_type'].shift(1)
        group['direction_changed'] = (group['direction_type'] != group['prev_direction']) & group['prev_direction'].notna()
        
        change_points = group[group['direction_changed']]
        
        for idx, row in change_points.iterrows():
            # The record before the change is the "arrival" or "last seen" in previous direction
            # The current record is the "departure" or "first seen" in new direction
            
            # Find the last record in the previous direction
            prev_records = group[group['last_rec_time'] < row['last_rec_time']]
            if prev_records.empty:
                continue
            
            last_record_prev = prev_records.iloc[-1]
            first_record_new = row
            
            turnaround_time = (first_record_new['last_rec_time'] - last_record_prev['last_rec_time']).total_seconds()
            
            turnarounds.append({
                'train_number': train_no,
                'station_name': last_record_prev['station_name'], # Station where it was last seen
                'prev_direction': last_record_prev['direction_type'],
                'new_direction': first_record_new['direction_type'],
                'arrival_time': last_record_prev['last_rec_time'],
                'departure_time': first_record_new['last_rec_time'],
                'turnaround_time_min': turnaround_time / 60.0
            })
            
    if not turnarounds:
        print("No turnaround events detected in this data window.")
        return
        
    turn_df = pd.DataFrame(turnarounds)
    
    print(f"\n=== Turnaround Efficiency Analysis for {line_name} ===")
    print(turn_df['turnaround_time_min'].describe())
    
    print("\n--- Turnaround Events ---")
    print(turn_df[['train_number', 'station_name', 'turnaround_time_min', 'arrival_time', 'departure_time']].sort_values('turnaround_time_min'))

if __name__ == "__main__":
    analyze_turnaround("3호선")
