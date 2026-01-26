import pandas as pd
import os

def convert_planning_md_to_xlsx(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows = []
    current_row = None

    for line in lines:
        stripped_line = line.rstrip('\n')
        if not stripped_line.strip() and not current_row:
            continue
            
        parts = stripped_line.split('\t')
        
        # 새로운 행 시작 기준: 탭이 1개 이상 있고, 
        # 첫 번째 열이 비어있지 않거나 (새 카테고리)
        # 혹은 특정 키워드로 시작하는 경우
        
        # 조금 더 단순하게: 탭이 있으면 새로운 항목으로 간주하고, 
        # 탭이 없으면 이전 항목의 상세 내용에 추가
        
        if len(parts) >= 2:
            # 이전 행 저장
            if current_row:
                rows.append(current_row)
            
            # 새로운 행 초기화 (최대 3열)
            cat = parts[0].strip()
            content = parts[1] if len(parts) > 1 else ""
            reason = parts[2] if len(parts) > 2 else ""
            current_row = [cat, content, reason]
        else:
            # 탭이 없는 줄 처리
            if current_row:
                # '상세 내용'(인덱스 1)에 계속 추가함
                # 하지만 만약 '선정 이유'가 비어있지 않다면 어디에 추가할지 모호함.
                # 보통 이런 식의 문서는 상세 내용이 길어짐.
                if stripped_line.strip():
                    current_row[1] += "\n" + stripped_line
            else:
                # 문서 처음에 탭 없는 줄이 나오면 무시하거나 첫 행으로 생성
                if stripped_line.strip():
                    current_row = [stripped_line.strip(), "", ""]

    # 마지막 행 저장
    if current_row:
        rows.append(current_row)

    # 헤더 제외 (첫 줄이 헤더인 경우 처리)
    if rows and rows[0][0] == '구분':
        header = rows[0]
        data = rows[1:]
    else:
        header = ['구분', '상세 내용', '선정 이유']
        data = rows

    df = pd.DataFrame(data, columns=header)
    
    # 출력 경로 확인 및 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 엑셀 저장 시 셀 내 줄바꿈 허용 설정
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        # 나중에 스타일 조정이 필요할 수 있지만 지금은 기본 저장
    
    print(f"Excel file created: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(BASE_DIR, '..', 'data', '만들어2.md')
    output_file = os.path.join(BASE_DIR, '..', 'data', '프로젝트_기획_상세.xlsx')
    convert_planning_md_to_xlsx(input_file, output_file)
