import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import os

# 폰트 설정 (Mac OS의 AppleGothic 사용)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def extract_sexual_violence_data(file_path, year):
    df = pd.read_excel(file_path, sheet_name=0)
    header_row_idx = -1
    for i, row in df.iterrows():
        if any('1월' in str(val) for val in row.values):
            header_row_idx = i
            break
    
    if header_row_idx != -1:
        df = pd.read_excel(file_path, sheet_name=0, header=header_row_idx + 1)
    
    mask = df.apply(lambda row: row.astype(str).str.contains('성폭력').any(), axis=1)
    target_rows = df[mask]
    
    if target_rows.empty:
        return None
    
    target_row = target_rows.iloc[0]
    months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    data = []
    
    for month in months:
        actual_col = None
        for col in df.columns:
            if month in str(col):
                actual_col = col
                break
        
        if actual_col:
            val = target_row[actual_col]
            if isinstance(val, str):
                val = float(val.replace(',', ''))
            data.append({'Month': f"{year}-{months.index(month)+1:02d}", 'Count': val})
    
    return pd.DataFrame(data)

df23 = extract_sexual_violence_data('/Users/baeseungjae/Documents/GitHub/kdt_woongin/solo_project/hosin/data/2023_범죄발생_월_범죄통계.xlsx', 2023)
df24 = extract_sexual_violence_data('/Users/baeseungjae/Documents/GitHub/kdt_woongin/solo_project/hosin/data/2024_범죄발생_월_범죄통계.xlsx', 2024)

if df23 is not None and df24 is not None:
    combined_df = pd.concat([df23, df24])
    combined_df['Month'] = pd.to_datetime(combined_df['Month'], format='%Y-%m')
    combined_df = combined_df.sort_values('Month')
    
    # 테마 설정
    sns.set_style("whitegrid", {"font.family": "AppleGothic"})
    plt.figure(figsize=(14, 7))
    
    main_color = '#E63946'
    highlight_color = '#1D3557'
    
    plt.plot(combined_df['Month'], combined_df['Count'], marker='o', color=main_color, linewidth=3, markersize=8, label='월별 성폭력 발생 건수')
    plt.fill_between(combined_df['Month'], combined_df['Count'], color=main_color, alpha=0.1)
    
    plt.title('2023-2024 월별 성폭력 범죄 발생 현황 및 추이', fontsize=20, pad=20, fontweight='bold')
    plt.xlabel('연월', fontsize=14)
    plt.ylabel('발생 건수', fontsize=14)
    
    for i, row in combined_df.iterrows():
        m = row['Month'].month
        if m in [6, 7, 8]:
            plt.scatter(row['Month'], row['Count'], color=highlight_color, s=150, zorder=5)
            plt.annotate(f"{int(row['Count'])}", (row['Month'], row['Count']), 
                         textcoords="offset points", xytext=(0,15), ha='center', 
                         fontsize=12, fontweight='bold', color=highlight_color)
        else:
            plt.annotate(f"{int(row['Count'])}", (row['Month'], row['Count']), 
                         textcoords="offset points", xytext=(0,10), ha='center', 
                         fontsize=10, color='gray')

    plt.axvline(x=pd.to_datetime('2024-01-01'), color='gray', linestyle='--', alpha=0.5)
    plt.text(pd.to_datetime('2023-06-01'), combined_df['Count'].max()*1.1, '2023년', fontsize=15, ha='center', color='gray')
    plt.text(pd.to_datetime('2024-06-01'), combined_df['Count'].max()*1.1, '2024년', fontsize=15, ha='center', color='gray')

    plt.ylim(0, combined_df['Count'].max() * 1.25)
    plt.legend(loc='upper left', fontsize=12)
    
    plt.xticks(combined_df['Month'], combined_df['Month'].dt.strftime('%y년 %m월'), rotation=45)
    
    plt.tight_layout()
    save_path = '/Users/baeseungjae/Documents/GitHub/kdt_woongin/solo_project/hosin/images/sexual_violence_trend.png'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300)
    print(f"Success: {save_path} saved with Korean fonts.")
else:
    print("Extraction failed.")
