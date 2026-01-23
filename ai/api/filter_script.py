import pandas as pd
import re

def is_korean(text):
    return bool(re.search('[가-힣]', str(text)))

def filter_data(file_path):
    df = pd.read_csv(file_path)
    
    # 1. Substance related keywords (English & Korean)
    substance_keywords = [
        'chalk', 'crush', 'powder', 'asmr', 'science', 'chemical', 'diet', 'health', 
        'experiment', 'cas no', 'formula', 'supplement', 'benefit', 'magnesio',
        'jual', 'gym', 'weightlifting', 'climbing chalk', 'reaction', 'blocks',
        '제조기술', '효능', '건강', '영양제', '화학', '성분', '부작용', '결핍', '탄산칼슘',
        '고순도', '추출', '제조', '바테라이트', '해수'
    ]
    
    # Brand related keywords (to save some that might be caught)
    brand_keywords = [
        '패션', '브랜드', '코디', '룩북', '하울', '택배깡', '팝업', '무신사', '지그재그', 
        '옷', '티셔츠', '롱슬리브', '비니', '모자', '가방', '위시리스트', '언박싱', '룩', '스타일'
    ]
    
    def should_remove(row):
        title = str(row['title']).lower()
        
        # Check if it has ANY substance keywords
        if any(k in title for k in substance_keywords):
            # Special case: if it has both brand and substance (unlikely for substance, but possible)
            # We prioritize removing if it's chemical.
            return True

        # Check for 'magnesium carbonate' in title (case insensitive)
        if 'magnesium carbonate' in title:
            # If it's English and doesn't explicitly look like the brand 'TANSNAMAGNESIUM'
            if 'tansnamagnesium' not in title and 'tansan' not in title:
                # If there's no Korean in it at all, it's very likely the substance.
                if not is_korean(row['title']):
                    return True
                # If there is Korean but no clothing keywords
                if not any(k in title for k in brand_keywords):
                    return True

        # 2. Language filtering: Remove non-Korean and non-English
        has_korean = is_korean(row['title'])
        if not has_korean:
            # Check for non-Latin characters
            # Allowing standard ASCII and some common symbols/emojis
            allowed_chars_regex = r'^[a-zA-Z0-9\s!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\]\{\}\;\:\'\"\\\|\,\.\<\>\/\?“”‘’°\~]*$'
            if not re.match(allowed_chars_regex, str(row['title'])):
                return True
            
            # Additional check: titles in other Latin languages (French, Spanish, Indonesian)
            # If it's pure English but has Indonesian/etc. words like "jual", it was already caught.
            # But let's be careful. If it doesn't look like English/Korean fashion, remove.
            # In this dataset, most of what's left is either EN brand stuff or KR brand/other.
            pass

        return False

    # Apply filter
    mask = df.apply(lambda row: not should_remove(row), axis=1)
    filtered_df = df[mask]
    
    # Save back
    filtered_df.to_csv(file_path, index=False)
    print(f"Original rows: {len(df)}")
    print(f"Filtered rows: {len(filtered_df)}")

if __name__ == "__main__":
    filter_data('/Users/baeseungjae/Documents/GitHub/kdt_woongin/ai/api/youtube_탄산마그네슘_results.csv')
