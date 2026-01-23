import json
import os
from datetime import datetime
from supabase import create_client, Client
import sys
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'config'))

from settings import settings

class DatabaseManager:
    def __init__(self):
        self.local_storage_path = str(PROJECT_ROOT / "config" / "data" / "collected_results.json")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.local_storage_path), exist_ok=True)
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            print("Warning: Supabase credentials missing. Using local JSON storage.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except Exception:
                print("Invalid Supabase credentials. Using local JSON storage.")
                self.supabase = None

    def _save_local(self, data: dict, data_type: str):
        """Append data to local JSON file for fallback."""
        try:
            current_data = []
            if os.path.exists(self.local_storage_path):
                with open(self.local_storage_path, "r", encoding="utf-8") as f:
                    try:
                        current_data = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            entry = {
                "type": data_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            current_data.append(entry)
            
            with open(self.local_storage_path, "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Local save failed: {e}")
            return False

    def save_product(self, product_data: dict):
        """
        Upserts a product. Returns product ID (UUID) or product_url if local.
        """
        if not self.supabase:
            # Local Fallback
            if self._save_local(product_data, "product"):
                # Return URL as ID for local linking
                return product_data.get('product_url')
            return None
        
        try:
            response = self.supabase.table("zigzag_products").upsert(
                product_data, on_conflict="product_url"
            ).execute()
            
            if response.data:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"Error saving product: {e}")
            # Fallback to local on error
            self._save_local(product_data, "product")
            return product_data.get('product_url')

    def save_reviews(self, product_id, reviews: list):
        """
        Inserts reviews.
        """
        if not reviews:
            return

        # Add product_id to each review
        for r in reviews:
            r['product_id'] = product_id

        if not self.supabase:
            # Local Fallback
            self._save_local({"product_id": product_id, "reviews": reviews}, "reviews")
            print(f"Saved {len(reviews)} reviews locally.")
            return
        
        try:
            self.supabase.table("zigzag_reviews").insert(reviews).execute()
            print(f"Saved {len(reviews)} reviews for product {product_id}")
        except Exception as e:
            print(f"Error saving reviews: {e}")
            self._save_local({"product_id": product_id, "reviews": reviews}, "reviews")
