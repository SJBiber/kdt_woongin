import os
import time
import pandas as pd
from datetime import datetime, timedelta
from scraper import NaverBlogCrawler

def main():
    # 1. 설정
    # 수집하고 싶은 키워드
    keyword = "탕후루"
    # 수집 시작일
    start_date_str = "2025-01-17"
    # 수집 종료일
    end_date_str = "2026-01-16"
    # 저장 파일명
    output_file = f"{keyword}_blog_counts.csv"
    
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
    
    # 기존 파일이 있으면 마지막 날짜 확인 후 이어받기
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file)
            if not df_existing.empty:
                last_date_str = df_existing['date'].max()
                last_dt = datetime.strptime(last_date_str, "%Y-%m-%d")
                current_dt = last_dt + timedelta(days=1)
                print(f"[*] 기존 {output_file}을 발견했습니다. {last_date_str} 이후부터 수집을 재개합니다.")
            else:
                print(f"[*] 기존 {output_file}이 비어있어 처음부터 수집을 시작합니다.")
        except Exception as e:
            print(f"[!] 기존 파일을 읽는 중 오류가 발생했습니다: {e}")
            print("[*] 처음부터 수집을 시작합니다.")

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
