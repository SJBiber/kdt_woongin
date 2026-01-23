import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Matplotlib 한글 폰트 설정 (Mac OS AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
IMG_DIR = os.path.join(BASE_DIR, '..', 'images')

def extract_sexual_violence_data(file_path, year):
    """2023/2024 Excel 파일에서 성폭력 발생 건수 추출"""
    try:
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
        if target_rows.empty: return None
        
        target_row = target_rows.iloc[0]
        months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        data = []
        for i, month in enumerate(months):
            actual_col = next((col for col in df.columns if month in str(col)), None)
            if actual_col:
                val = target_row[actual_col]
                if isinstance(val, str): val = float(val.replace(',', ''))
                data.append({'Year': year, 'Month': i+1, 'Sexual_Violence': val})
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error extracting crime data for {year}: {e}")
        return None

def main():
    # 1. 데이터 수집 및 병합 (2023, 2024)
    all_data = []
    
    for year in [2023, 2024]:
        # 검색량 로드
        vol_file = os.path.join(DATA_DIR, f'키워드사운드_호신용품_검색량_{year}.xlsx')
        if not os.path.exists(vol_file): continue
        df_vol = pd.read_excel(vol_file)
        df_vol['날짜'] = pd.to_datetime(df_vol['날짜'])
        df_vol['월'] = df_vol['날짜'].dt.month
        monthly_vol = df_vol.groupby('월')['검색량'].sum().reset_index()
        monthly_vol.columns = ['Month', 'Search_Volume']
        monthly_vol['Year'] = year
        
        # 성폭력 데이터 로드
        crime_file = os.path.join(DATA_DIR, f'{year}_범죄발생_월_범죄통계.xlsx')
        df_crime = extract_sexual_violence_data(crime_file, year)
        
        # 사건 리스트(파급력) 데이터 로드 (주요 강력 범죄 기사 수)
        impact_file = os.path.join(DATA_DIR, '년도별_범죄_리스트.xlsx')
        try:
            df_impact = pd.read_excel(impact_file, sheet_name=str(year), skiprows=2)
            df_impact['월'] = df_impact['발생일'].str.extract(r'(\d+)월').astype(int)
            monthly_impact = df_impact.groupby('월').size().reindex(range(1, 13), fill_value=0).reset_index()
            monthly_impact.columns = ['Month', 'Major_Crime_Reports']
            monthly_impact['Year'] = year
            
            # 병합
            merged = pd.merge(monthly_vol, df_crime, on=['Year', 'Month'])
            merged = pd.merge(merged, monthly_impact, on=['Year', 'Month'])
            all_data.append(merged)
        except Exception as e:
            print(f"Error processing impact data for {year}: {e}")

    if not all_data:
        print("No data to analyze.")
        return
        
    df = pd.concat(all_data).reset_index(drop=True)
    
    # 2. 상관계수 계산
    corr_matrix = df[['Search_Volume', 'Sexual_Violence', 'Major_Crime_Reports']].corr()
    
    # 3. 시각화 (Heatmap)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', fmt='.2f', linewidths=0.5,
                xticklabels=['호신용품 검색량', '성폭력 발생 건수', '주요 범죄 보도 수'],
                yticklabels=['호신용품 검색량', '성폭력 발생 건수', '주요 범죄 보도 수'])
    plt.title('호신용품 검색량과 범죄 지표 간의 상관계수 (2023-2024)', fontsize=16, pad=20, fontweight='bold')
    plt.tight_layout()
    save_path = os.path.join(IMG_DIR, 'correlation_heatmap.png')
    plt.savefig(save_path, dpi=300)
    print(f"Saved: {save_path}")

    # 4. 시각화 (Scatter Plot with Regression Line)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # 검색량 vs 성폭력
    sns.regplot(data=df, x='Sexual_Violence', y='Search_Volume', ax=ax1, 
                scatter_kws={'alpha':0.6, 's':100, 'color':'#E63946'}, 
                line_kws={'color':'#1D3557'})
    ax1.set_title(f"검색량 vs 성폭력 발생 (r={corr_matrix.loc['Search_Volume', 'Sexual_Violence']:.2f})", fontsize=14, fontweight='bold')
    ax1.set_xlabel('성폭력 발생 건수 (월)', fontsize=12)
    ax1.set_ylabel('호신용품 검색량 (월)', fontsize=12)
    
    # 검색량 vs 주요 범죄 보도 수
    sns.regplot(data=df, x='Major_Crime_Reports', y='Search_Volume', ax=ax2,
                scatter_kws={'alpha':0.6, 's':100, 'color':'#457B9D'},
                line_kws={'color':'#1D3557'})
    ax2.set_title(f"검색량 vs 주요 범죄 보도 수 (r={corr_matrix.loc['Search_Volume', 'Major_Crime_Reports']:.2f})", fontsize=14, fontweight='bold')
    ax2.set_xlabel('주요 강력 범죄 보도 수 (월)', fontsize=12)
    ax2.set_ylabel('호신용품 검색량 (월)', fontsize=12)
    
    plt.suptitle('호신용품 검색량과 범죄 지표의 상관관계 분석', fontsize=20, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_path_scatter = os.path.join(IMG_DIR, 'correlation_scatter.png')
    plt.savefig(save_path_scatter, dpi=300)
    print(f"Saved: {save_path_scatter}")

if __name__ == "__main__":
    main()
