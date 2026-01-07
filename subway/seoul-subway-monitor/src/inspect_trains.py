import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_client import SubwayDB

def inspect_train_paths():
    db = SubwayDB()
    response = db.supabase.table(db.table_name).select("*").order("last_rec_time").execute()
    df = pd.DataFrame(response.data)
    
    # Sort by train and time
    df = df.sort_values(['train_number', 'last_rec_time'])
    
    found = False
    for train_no, group in df.groupby('train_number'):
        if group['direction_type'].nunique() > 1 or group['dest_station_name'].nunique() > 1:
            print(f"\n--- Train {train_no} showed change ---")
            print(group[['last_rec_time', 'station_name', 'direction_type', 'dest_station_name', 'train_status']])
            found = True
            # Print only first few to not overwhelm
            if train_no == list(df['train_number'].unique())[10]: # Stop after a few
                break

    if not found:
        print("No turnaround patterns detected yet. Maybe the data window is too short.")
        # Let's see some sample data for one train
        sample_train = df['train_number'].iloc[0]
        print(f"\nSample data for train {sample_train}:")
        print(df[df['train_number'] == sample_train][['last_rec_time', 'station_name', 'direction_type', 'dest_station_name', 'train_status']])

if __name__ == "__main__":
    inspect_train_paths()
