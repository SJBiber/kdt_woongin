import asyncio
from src.collector import ZigzagCollector
from datetime import datetime

async def main():
    print(f"--- [{datetime.now()}] Zigzag Data Collector ---")
    
    # 1. Input Category (Arguments or User Input)
    import sys
    if len(sys.argv) > 1:
        category_name = sys.argv[1]
    else:
        try:
            if not sys.stdin.isatty():
                 category_name = "상의"
                 print(f"Non-interactive mode detected. Defaulting to '{category_name}'.")
            else:
                 category_name = input("수집할 대항목 카테고리를 입력하세요 (예: 상의, 아우터, 팬츠): ").strip()
                 if not category_name:
                    category_name = "상의"
                    print(f"No input provided. Defaulting to '{category_name}'.")
        except Exception as e:
            category_name = "상의" 
            print(f"Input error ({e}). Defaulting to '{category_name}'.")

    print(f"Target Category: {category_name}")
    print("Initializing Collector...")
    
    collector = ZigzagCollector()
    
    # Run the collection process
    await collector.run(category_name)
    
    print(f"--- [{datetime.now()}] Collection Completed ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
