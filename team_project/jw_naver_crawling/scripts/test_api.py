import requests
import json

def get_naver_blog_count(keyword):
    url = "https://section.blog.naver.com/ajax/SearchList.naver"
    
    params = {
        "countPerPage": "7",
        "currentPage": "1",
        "startDate": "",
        "endDate": "",
        "keyword": keyword,
        "orderBy": "sim"
    }
    
    from urllib.parse import quote
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword={quote(keyword)}",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            return None
            
        content = response.text
        # Debug: check response content
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            return None

        # Naver AJAX API often adds security prefixes like )]}', or )]}'\n
        start_idx = content.find('{')
        if start_idx == -1:
            print("No JSON object found in response.")
            print("Response Content Preview:")
            print(content[:500])
            return None
            
        clean_content = content[start_idx:].strip()
        
        try:
            data = json.loads(clean_content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print("Cleaned Content Preview:")
            print(clean_content[:500])
            return None
        
        # 결과에서 totalCount 추출
        total_count = data.get("result", {}).get("totalCount", 0)
        return total_count
    except Exception as e:
        print(f"Error fetching count for '{keyword}': {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    search_keyword = "두쫀쿠"
    count = get_naver_blog_count(search_keyword)
    if count is not None:
        print(f"키워드 '{search_keyword}'의 총 검색 결과 수: {count:,}건")
