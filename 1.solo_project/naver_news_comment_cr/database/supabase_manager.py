"""
Supabase 데이터베이스 연결 및 관리 모듈
"""

from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from typing import List, Dict, Any
from datetime import datetime


class SupabaseManager:
    """Supabase 데이터베이스 관리 클래스"""
    
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.comment_table = "naver_news_comments"
        self.article_table = "naver_news_articles"
        print(f"✅ Supabase 연결 완료")
    
    def insert_comment(self, comment_data: Dict[str, Any]) -> bool:
        """
        단일 댓글 데이터 삽입
        
        Args:
            comment_data: 댓글 데이터 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            response = self.client.table(self.comment_table).insert(comment_data).execute()
            return True
        except Exception as e:
            print(f"❌ 댓글 삽입 실패: {e}")
            return False
    
    def insert_comments_batch(self, comments: List[Dict[str, Any]]) -> int:
        """
        여러 댓글 데이터를 배치로 삽입
        
        Args:
            comments: 댓글 데이터 리스트
            
        Returns:
            성공적으로 삽입된 댓글 수
        """
        if not comments:
            return 0
        
        try:
            response = self.client.table(self.comment_table).insert(comments).execute()
            inserted_count = len(response.data) if response.data else 0
            print(f"✅ {inserted_count}개 댓글 삽입 완료")
            return inserted_count
        except Exception as e:
            print(f"❌ 배치 삽입 실패: {e}")
            # 개별 삽입 시도
            success_count = 0
            for comment in comments:
                if self.insert_comment(comment):
                    success_count += 1
            print(f"⚠️  개별 삽입으로 {success_count}/{len(comments)}개 저장 완료")
            return success_count
    
    def comment_exists(self, comment_id: str) -> bool:
        """
        댓글 ID가 이미 존재하는지 확인
        
        Args:
            comment_id: 확인할 댓글 ID
            
        Returns:
            존재 여부
        """
        try:
            response = self.client.table(self.comment_table)\
                .select("comment_id")\
                .eq("comment_id", comment_id)\
                .execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"❌ 댓글 존재 확인 실패: {e}")
            return False
    
    def get_comments_by_news_id(self, news_id: str) -> List[Dict[str, Any]]:
        """
        특정 뉴스의 모든 댓글 조회
        
        Args:
            news_id: 뉴스 ID
            
        Returns:
            댓글 리스트
        """
        try:
            response = self.client.table(self.comment_table)\
                .select("*")\
                .eq("news_id", news_id)\
                .execute()
            return response.data
        except Exception as e:
            print(f"❌ 댓글 조회 실패: {e}")
            return []
    
    def insert_article(self, article_data: Dict[str, Any]) -> bool:
        """단일 뉴스 기사 삽입"""
        try:
            self.client.table(self.article_table).insert(article_data).execute()
            return True
        except Exception as e:
            if "duplicate key value" not in str(e):
                print(f"❌ 기사 삽입 실패: {e}")
            return False

    def insert_articles_batch(self, articles: List[Dict[str, Any]]) -> int:
        """여러 뉴스 기사 배기 삽입"""
        if not articles: return 0
        try:
            response = self.client.table(self.article_table).upsert(articles, on_conflict="news_id").execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"❌ 기사 배치 삽입 실패: {e}")
            return 0

    def article_exists(self, news_id: str) -> bool:
        """뉴스 ID 존재 여부 확인"""
        try:
            res = self.client.table(self.article_table).select("news_id").eq("news_id", news_id).execute()
            return len(res.data) > 0
        except:
            return False


if __name__ == "__main__":
    # 테스트 코드
    db = SupabaseManager()
    print("데이터베이스 연결 테스트 완료")
