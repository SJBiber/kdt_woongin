import os
import time
import pandas as pd
from datetime import datetime, timedelta
from scraper import NaverBlogCrawler

def main():
    # 1. 설정
    keyword = "마라탕"
    start_date_str = "2018-08-01"
    end_date_str = "2023-08-01"
    output_file = "maratang_blog_counts.csv"
    
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    total_days = (end_dt - start_dt).days + 1
    
    print(f"=== {keyword} 네이버 블로그 포스팅 수집 시작 (CSV 전용) ===")
    print(f"기간: {start_date_str} ~ {end_date_str} ({total_days}일)")
    print(f"저장 파일: {output_file}")
    print("-" * 40)

    # 2. 초기화
    crawler = NaverBlogCrawler()
    
    results = []
    current_dt = start_dt
    
    # 기존 파일이 있으면 삭제하고 새로 시작 (요청하신 새로운 시작을 위해)
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"[*] 기존 {output_file} 파일을 삭제하고 새로 수집을 시작합니다.")

    # 3. 루프 실행
    try:
        while current_dt <= end_dt:
            date_str = current_dt.strftime("%Y-%m-%d")
            print(f"\n[+] 날짜: {date_str}", end=" ", flush=True)
            
            count = crawler.get_blog_count(keyword, start_date=date_str, end_date=date_str)
            
            if count is not None:
                print(f"-> {count:,}건")
                data_row = {
                    "date": date_str,
                    "keyword": keyword,
                    "total_count": count
                }
                results.append(data_row)
                
                # CSV 실시간 저장 (데이터 유실 방지)
                df = pd.DataFrame([data_row])
                if not os.path.exists(output_file):
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                else:
                    df.to_csv(output_file, mode='a', index=False, header=False, encoding='utf-8-sig')
            else:
                print("-> 실패")
            
            # 요청 간 딜레이 (0.5초)
            time.sleep(0.5)
            current_dt += timedelta(days=1)
            
    except KeyboardInterrupt:
        print("\n\n[!] 사용자에 의해 중단되었습니다. 현재까지의 데이터는 저장되었습니다.")

    print(f"\n[+] 수집 완료. 결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()
