import pandas as pd
from database import SupabaseManager
import sys
import io

# 표준 출력을 UTF-8로 재설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def upload_csv_to_db(csv_path):
    try:
        # DB 매니저 초기화
        db = SupabaseManager()
        
        # CSV 로드
        print(f"[*] {csv_path} 파일을 읽는 중...")
        df = pd.read_csv(csv_path)
        
        # 데이터 업로드
        total_rows = len(df)
        print(f"[*] 총 {total_rows}개의 데이터를 DB에 업로드합니다...")
        
        success_count = 0
        for _, row in df.iterrows():
            data = {
                "date": row['date'],
                "keyword": row['keyword'],
                "total_count": int(row['total_count'])
            }
            
            res = db.insert_blog_trend(data)
            if res:
                success_count += 1
                if success_count % 50 == 0:
                    print(f"[...] 진행 중: {success_count}/{total_rows}")
        
        print(f"\n[+] 업로드 완료! (성공: {success_count}/{total_rows})")
        
    except Exception as e:
        print(f"[!] 오류 발생: {e}")

if __name__ == "__main__":
    csv_file = "mara_counts.csv"
    upload_csv_to_db(csv_file)
