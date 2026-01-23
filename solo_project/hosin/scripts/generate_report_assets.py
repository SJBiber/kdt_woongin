import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Matplotlib 한글 폰트 설정 (Mac 기준)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
IMG_DIR = os.path.join(BASE_DIR, '..', 'images')

def generate_crime_trend_charts():
    """연도별 범죄 발생 건수 바 차트 생성"""
    years = [2023, 2024, 2025]
    for year in years:
        try:
            file_path = os.path.join(DATA_DIR, '년도별_범죄_리스트.xlsx')
            df = pd.read_excel(file_path, sheet_name=str(year), skiprows=2, usecols=range(1,7))
            df['월'] = df['발생일'].str.extract(r'(\d+)월').astype(int)
            monthly_crime = df.groupby('월')['파급력'].count()
            
            plt.figure(figsize=(10, 6))
            max_val = monthly_crime.max()
            colors = ['red' if v == max_val else 'blue' for v in monthly_crime.values]
            
            bars = plt.bar(monthly_crime.index, monthly_crime.values, color=colors)
            plt.title(f'{year}년도 주요 범죄 발생 건수 추이', fontweight='bold', fontsize=15)
            plt.xlabel('월')
            plt.ylabel('범죄 기사 개수')
            plt.xticks(range(1, 13))
            plt.ylim(0, max_val + 2)
            
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, 
                         f'{int(height)}개', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join(IMG_DIR, f'crime_{year}.png'))
            plt.close()
            print(f"Created crime_{year}.png in images/")
        except Exception as e:
            print(f"Error generating crime chart for {year}: {e}")

def generate_total_volume_charts():
    """연도별 총 검색량 바 차트 생성"""
    years = [2023, 2024, 2025]
    for year in years:
        file_path = os.path.join(DATA_DIR, f'키워드사운드_호신용품_검색량_{year}.xlsx')
        if not os.path.exists(file_path): continue
        
        df = pd.read_excel(file_path)
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['월'] = df['날짜'].dt.month
        monthly_total = df.groupby('월')['검색량'].sum()
        
        plt.figure(figsize=(10, 6))
        max_val = monthly_total.max()
        colors = ['red' if v == max_val else 'skyblue' for v in monthly_total.values]
        
        bars = plt.bar(monthly_total.index, monthly_total.values, color=colors)
        plt.title(f'{year}년 호신용품 월별 총 검색량 (절대 수치)', fontweight='bold', fontsize=15)
        plt.xlabel('월')
        plt.ylabel('총 검색량 (건)')
        plt.xticks(range(1, 13))
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, 
                     f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(IMG_DIR, f'volume_{year}.png'))
        plt.close()
        print(f"Created volume_{year}.png in images/")

def generate_gender_comparison_charts():
    """성별 검색량 나란히 비교 차트 생성"""
    years = [2023, 2024, 2025]
    ratio_file = os.path.join(DATA_DIR, '성별_비율_데이터.xlsx')
    
    try:
        ratio_xl = pd.ExcelFile(ratio_file)
    except Exception as e:
        print(f"Error loading ratio file: {e}")
        return

    for year in years:
        vol_file = os.path.join(DATA_DIR, f'키워드사운드_호신용품_검색량_{year}.xlsx')
        if not os.path.exists(vol_file): continue
        
        df_vol = pd.read_excel(vol_file)
        df_vol['날짜'] = pd.to_datetime(df_vol['날짜'])
        df_vol['월'] = df_vol['날짜'].dt.month
        monthly_total = df_vol.groupby('월')['검색량'].sum()
        
        sheet_name = f'{year}년도'
        df_ratio = pd.read_excel(ratio_file, sheet_name=sheet_name)
        df_ratio.set_index('월', inplace=True)
        
        male_vol = []
        female_vol = []
        months = range(1, 13)
        
        for m in months:
            total = monthly_total.get(m, 0)
            m_ratio = df_ratio.loc[m, '남'] if m in df_ratio.index else 0.5
            f_ratio = df_ratio.loc[m, '여'] if m in df_ratio.index else 0.5
            male_vol.append(round(total * m_ratio))
            female_vol.append(round(total * f_ratio))
        
        plt.figure(figsize=(15, 8))
        x = np.arange(1, 13)
        width = 0.35
        
        plt.bar(x - width/2, male_vol, width, label='남성', color='skyblue', alpha=0.9)
        plt.bar(x + width/2, female_vol, width, label='여성', color='salmon', alpha=0.9)
        
        plt.title(f'{year}년 성별 호신용품 검색 화력 비교 (월별 정밀 비율 적용)', fontweight='bold', fontsize=18)
        plt.xlabel('월', fontsize=12)
        plt.ylabel('검색 건수', fontsize=12)
        plt.xticks(x)
        plt.legend(fontsize=12)
        
        for i in range(len(x)):
            plt.text(x[i] - width/2, male_vol[i], f'{int(male_vol[i]):,}', ha='center', va='bottom', fontsize=9)
            plt.text(x[i] + width/2, female_vol[i], f'{int(female_vol[i]):,}', ha='center', va='bottom', fontsize=9)
            
        plt.ylim(0, max(max(male_vol), max(female_vol)) * 1.15)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(IMG_DIR, f'gender_compare_{year}.png'))
        plt.close()
        print(f"Created gender_compare_{year}.png in images/")

def generate_monthly_gender_ratio_charts():
    """연도별 월별 성별 비중 차트 생성"""
    years = [2023, 2024, 2025]
    ratio_file = os.path.join(DATA_DIR, '성별_비율_데이터.xlsx')
    
    for year in years:
        sheet_name = f'{year}년도'
        try:
            df = pd.read_excel(ratio_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error loading {sheet_name}: {e}")
            continue
            
        plt.figure(figsize=(12, 6))
        x = df['월']
        
        plt.bar(x, df['남'] * 100, label='남성 비중', color='skyblue', alpha=0.8)
        plt.bar(x, df['여'] * 100, bottom=df['남'] * 100, label='여성 비중', color='salmon', alpha=0.8)
        
        plt.title(f'{year}년 월별 성별 검색 비중 변화 (%)', fontweight='bold', fontsize=16)
        plt.xlabel('월')
        plt.ylabel('비중 (%)')
        plt.xticks(x)
        plt.ylim(0, 115)
        plt.axhline(50, color='gray', linestyle='--', alpha=0.5)
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        
        for i, row in df.iterrows():
            plt.text(row['월'], row['남']*100/2, f"{row['남']*100:.0f}%", ha='center', va='center', color='white', fontweight='bold')
            plt.text(row['월'], row['남']*100 + row['여']*100/2, f"{row['여']*100:.0f}%", ha='center', va='center', color='white', fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(IMG_DIR, f'gender_ratio_{year}.png'))
        plt.close()
        print(f"Created gender_ratio_{year}.png in images/")

def generate_impact_combined_charts():
    """주요 강력 범죄 키워드별 '최상' 사건 수와 검색량을 시각화 (impact_volume_YYYY.png)"""
    years = [2023, 2024, 2025]
    crime_file = os.path.join(DATA_DIR, '년도별_범죄_리스트.xlsx')
    # 필터링할 핵심 키워드
    target_keywords = ['납치', '테러', '협박', '묻지마', '살인', '흉기', '난동']
    
    for year in years:
        vol_file = os.path.join(DATA_DIR, f'키워드사운드_호신용품_검색량_{year}.xlsx')
        if not os.path.exists(vol_file): continue
        
        # 1. 검색량 데이터 로드
        df_vol = pd.read_excel(vol_file)
        df_vol['날짜'] = pd.to_datetime(df_vol['날짜'])
        df_vol['월'] = df_vol['날짜'].dt.month
        monthly_vol = df_vol.groupby('월')['검색량'].sum()
        
        # 2. 범죄 데이터 필터링 (키워드 기반 + '최상' 등급만)
        try:
            df_crime = pd.read_excel(crime_file, sheet_name=str(year), skiprows=2)
            df_crime['월'] = df_crime['발생일'].str.extract(r'(\d+)월').astype(int)
            
            # 키워드 필터링
            pattern = '|'.join(target_keywords)
            df_filtered = df_crime[df_crime['사건명 및 내용'].str.contains(pattern, na=False, case=False)]
            
            # '최상' 등급만 카운트
            monthly_impact = df_filtered[df_filtered['파급력'] == '최상'].groupby('월').size().reindex(range(1, 13), fill_value=0)
        except Exception as e:
            print(f"Error filtering crime data for {year}: {e}")
            monthly_impact = pd.Series(0, index=range(1, 13))

        # 3. 그래프 생성
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        # 축 1: 검색량 (Bar)
        ax1.set_xlabel('월', fontsize=12)
        ax1.set_ylabel('월간 총 검색량 (건)', color='steelblue', fontsize=12)
        bars = ax1.bar(monthly_vol.index, monthly_vol.values, color='skyblue', alpha=0.4, label='호신용품 검색량')
        ax1.tick_params(axis='y', labelcolor='steelblue')
        
        # 검색량 수치 표시 (막대 위에)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (monthly_vol.max()*0.01), f'{int(height):,}', 
                     ha='center', va='bottom', fontsize=9, color='steelblue', fontweight='bold')

        # 축 2: '최상' 파급력 범죄 보도 수 (Single Line)
        ax2 = ax1.twinx()
        color_line = 'crimson'
        ax2.set_ylabel("'최상' 등급 강력 범죄 보도 수 (건)", color=color_line, fontsize=12)
        
        line = ax2.plot(monthly_impact.index, monthly_impact.values, color=color_line, 
                        marker='o', linewidth=3, markersize=10, label="핵심 범죄 보도 [최상] (테러/묻지마 등)")
        ax2.tick_params(axis='y', labelcolor=color_line)
        
        # Y축 눈금 설정 (정수 단위)
        ax2.set_yticks(range(0, int(monthly_impact.max()) + 2))

        # 범죄 건수 수치 표시 (점 위에)
        for i, v in enumerate(monthly_impact.values):
            if v > 0:
                ax2.text(i+1, v + 0.15, f'{v}건', ha='center', va='bottom', 
                         fontsize=11, color=color_line, fontweight='bold')

        plt.title(f"{year}년 국가적 재난 수준 범죄 이슈와 검색량 상관관계", fontweight='bold', fontsize=18, pad=20)
        ax1.set_xticks(range(1, 13))
        
        # 범례 설정
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')

        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(IMG_DIR, f'impact_volume_{year}.png'))
        plt.close()
        print(f"Created highest-only impact_volume_{year}.png")

if __name__ == "__main__":
    generate_crime_trend_charts()
    generate_total_volume_charts()
    generate_gender_comparison_charts()
    generate_monthly_gender_ratio_charts()
    generate_impact_combined_charts()
