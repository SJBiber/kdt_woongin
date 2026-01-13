import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# 환경 변수 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../.env")

if os.path.exists(env_path):
    load_dotenv(env_path)

class GeminiAnalyzer:
    def __init__(self):
        # API 키 설정
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY is missing in .env file.")
        
        # Gemini 설정
        genai.configure(api_key=self.gemini_key)
        # 사용자 요청에 따라 gemini-flash-latest 사용
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
        # Supabase 클라이언트 초기화
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def analyze_content(self, content):
        """Gemini를 사용하여 블로그 본문 분석"""
        prompt = f"""
        당신은 데이터 분석 전문가입니다. 다음 블로그 게시글 내용을 분석하여 지정된 JSON 형식으로 요약해 주세요.
        내용에 관련 정보가 없는 경우 "정보 없음"이라고 기재해 주세요. 반드시 JSON 형식만 반환하세요.

        [분석할 내용]
        {content}

        [반환 형식 지침]
        1. "region": 상가의 정확한 위치(도로명 주소 또는 지점명)를 기입하세요.
        2. "price_range": 본문의 가격 정보를 추출하세요, 반드시 개당 0000원으로 부탁함 (정보 없으면 "정보 없음")
        3. "price_feedback": 반드시 [비쌈, 저렴, 보통] 중 하나만 선택하세요.
        4. "taste_rating": 반드시 [매우 맛있음, 맛있음, 보통, 맛없음, 매우 맛없음] 중 하나만 선택하세요.
        5. "visit_again": 반드시 [있음, 고려, 없음] 중 하나만 선택하세요.
        6. "visit_reason": 위 결정의 이유(웨이팅, 가격, 맛 등)를 기입하세요.
        7. "summary": 전체 내용을 한 줄로 요약하세요.

        반드시 위 7가지 필드를 포함한 JSON 형식만 반환하세요.
        """
        try:
            response = self.model.generate_content(prompt)
            # JSON만 추출하기 위한 정규화
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Analysis Error: {e}")
            return None

    def run_batch_analysis(self, limit=10):
        """AI 분석이 안된 데이터를 가져와서 분석 진행"""
        print(f"Fetching up to {limit} records for analysis...")
        
        # ai_analysis가 null인 데이터 가져오기
        records = self.supabase.table("blog_reviews")\
            .select("id, clean_content")\
            .is_("ai_analysis", "null")\
            .limit(limit)\
            .execute()
        
        if not records.data:
            print("No new records to analyze.")
            return

        for record in records.data:
            record_id = record['id']
            content = record['clean_content']
            
            if not content or len(content) < 50:
                print(f"Skipping record {record_id} due to short content.")
                continue
                
            print(f"Analyzing record {record_id}...")
            analysis_result = self.analyze_content(content[:4000]) # 토큰 제한 고려
            
            if analysis_result:
                # Supabase 업데이트
                self.supabase.table("blog_reviews")\
                    .update({"ai_analysis": analysis_result})\
                    .eq("id", record_id)\
                    .execute()
                print(f"Successfully updated record {record_id}")
                # 분당 호출 제한(RPM 5회)을 고려하여 12초 이상 대기
                print("Waiting 13 seconds for quota...")
                time.sleep(13)
            else:
                # 에러 발생 시(주로 할당량) 조금 더 길게 대기 후 다음 레코드 시도
                print("Analysis failed, waiting 20 seconds before retry...")
                time.sleep(20)

if __name__ == "__main__":
    analyzer = GeminiAnalyzer()
    
    # 한 번에 20개씩 분석 진행
    analyzer.run_batch_analysis(limit=20)
