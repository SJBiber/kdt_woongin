import os
import json
import re
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경 변수 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../.env")
load_dotenv(env_path)

class LocalReviewAnalyzer:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase Credentials are missing in .env file.")
            
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # 키워드 사전 정의
        self.lexicon = {
            "price": {
                "저렴": ["가성비", "저렴", "싼", "착한 가격", "혜자", "부담 없는"],
                "비쌈": ["비싼", "사악", "가격대 있는", "양에 비해", "비싸다", "고가"],
                "보통": ["적당", "보통", "무난", "나쁘지 않은 가격"]
            },
            "taste": {
                "매우 맛있음": ["최고", "인생", "존맛", "역대급", "대박", "미쳤다"],
                "맛있음": ["맛있", "추천", "괜찮", "굿", "성공적"],
                "보통": ["보통", "평범", "무난", "나쁘지 않은"],
                "맛없음": ["그저 그런", "쏘쏘", "제 스타일은 아닌", "아쉬운"],
                "매우 맛없음": ["실망", "다시는 안", "돈 아까운", "최악"]
            },
            "visit": {
                "있음": ["재방문", "또 갈", "자주 갈", "단골", "생각날"],
                "고려": ["한두번은", "가끔", "근처라면", "생각해보면"],
                "없음": ["다시는", "안 갈", "웨이팅하면서까지", "절대"]
            }
        }

    def extract_price(self, text):
        """본문에서 '두바이 쿠키' 키워드 근처의 가격 패턴만 정밀 추출 및 정수 반환 (1,000~11,000)"""
        sentences = re.split(r'[.\n!]', text)
        product_keywords = ["두바이", "쫀득", "쿠키", "두쫀쿠", "초콜릿쿠키"]
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in product_keywords):
                price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*원', sentence)
                for price_str in price_matches:
                    price_val = int(price_str.replace(",", ""))
                    if 1000 <= price_val <= 11000:
                        return price_val # 정수형으로 반환
                        
        for keyword in product_keywords:
            pattern = rf"{keyword}.{{0,30}}?(\d{{1,3}}(?:,\d{{3}})*)\s*원"
            match = re.search(pattern, text)
            if match:
                price_val = int(match.group(1).replace(",", ""))
                if 1000 <= price_val <= 11000:
                    return price_val # 정수형으로 반환

        return None # 정보 없음 시 None(DB에서는 null) 반환

    def match_lexicon(self, text, category, default="보통"):
        """사전 기반 키워드 매칭"""
        for label, keywords in self.lexicon[category].items():
            if any(k in text for k in keywords):
                return label
        return default

    def analyze_locally(self, record):
        """로컬 룰 기반 분석 실행"""
        text = record['clean_content']
        
        # 1. 지역 추출
        region = record.get('address', '정보 없음')
        
        # 2. 가격 정보 (정수형)
        product_price = self.extract_price(text)
        
        # 3. 가격 피드백 (기본값: 평범)
        price_feedback = self.match_lexicon(text, "price", "평범")
        
        # 4. 맛 평가 (기본값: 보통)
        taste_rating = self.match_lexicon(text, "taste", "보통")
        
        # 5. 재방문 의사 (기본값: 없음)
        visit_again = self.match_lexicon(text, "visit", "없음")
        
        # 6. 방문 사유 간소화
        visit_reason = f"{taste_rating} 평가 및 {price_feedback} 가격대"

        return {
            "review_id": record['id'],
            "region": region,
            "product_price": product_price,  # 컬럼명 변경 및 정수 데이터 대입
            "price_feedback": price_feedback,
            "taste_rating": taste_rating,
            "visit_again": visit_again,
            "visit_reason": visit_reason
        }

    def run_analysis(self, limit=100):
        print(f"Fetching {limit} records for Local Analysis...")
        
        # 1. 이미 분석된 review_id 목록 가져오기
        analyzed_records = self.supabase.table("review_analysis_result")\
            .select("review_id").execute()
        analyzed_ids = {r['review_id'] for r in analyzed_records.data}
        print(f"Total analyzed records in DB: {len(analyzed_ids)}")

        # 2. 원본 리뷰 가져오기
        records = self.supabase.table("blog_review").select("*").limit(limit).execute()
        
        if not records.data:
            print("No records found in blog_review.")
            return

        processed_count = 0
        for record in records.data:
            # 3. 방어 로직: 이미 분석된 ID는 건너뛰기
            if record['id'] in analyzed_ids:
                continue
                
            print(f"Analyzing {record['id']}: {record['title'][:30]}...")
            idx_result = self.analyze_locally(record)
            
            # 4. 별도의 결과 테이블에 저장
            try:
                self.supabase.table("review_analysis_result").upsert(idx_result).execute()
                print(f"✅ Saved analysis for ID {record['id']}")
                processed_count += 1
            except Exception as e:
                print(f"❌ DB Error: {e}")
        
        print(f"\n✨ Analysis cycle completed. New records processed: {processed_count}")

if __name__ == "__main__":
    analyzer = LocalReviewAnalyzer()
    # 1000개 수집된 데이터에 맞춰 분석 한도를 늘립니다.
    analyzer.run_analysis(limit=1000)
