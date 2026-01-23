import pandas as pd
import io
import re

def convert_md_to_xlsx(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 연도별 세션 찾기 (숫자 4자리 + 년도)
    sessions = re.split(r'(\d{4}\s*년도)', content)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i in range(1, len(sessions), 2):
            year_header = sessions[i].strip()
            year = re.search(r'\d{4}', year_header).group()
            data_block = sessions[i+1].strip()
            
            if not data_block:
                continue
            
            # 데이터 파싱
            df = pd.read_csv(io.StringIO(data_block), sep=r'\s+')
            
            # 시트 이름 설정
            sheet_name = f'{year}년도'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Added sheet: {sheet_name}")

if __name__ == "__main__":
    convert_md_to_xlsx('../data/만들어.md', '../data/성별_비율_데이터.xlsx')
