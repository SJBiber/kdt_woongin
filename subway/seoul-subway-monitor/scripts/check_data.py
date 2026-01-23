import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db_client import SubwayDB

def check_data():
    db = SubwayDB()
    
    # Check total row count
    try:
        response = db.supabase.table(db.table_name).select("*", count="exact").limit(1).execute()
        total_count = response.count
        print(f"Total rows in {db.table_name}: {total_count}")
        
        if total_count > 0:
            # Check latest and oldest data
            latest = db.supabase.table(db.table_name).select("last_rec_time").order("last_rec_time", desc=True).limit(1).execute()
            oldest = db.supabase.table(db.table_name).select("last_rec_time").order("last_rec_time", desc=False).limit(1).execute()
            
            print(f"Latest record: {latest.data[0]['last_rec_time']}")
            print(f"Oldest record: {oldest.data[0]['last_rec_time']}")
            
            # Check number of trains
            trains = db.supabase.table(db.table_name).select("train_number").execute()
            unique_trains = len(set(t['train_number'] for t in trains.data))
            print(f"Number of unique trains: {unique_trains}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
