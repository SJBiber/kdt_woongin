import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from collections import defaultdict

# .env 로드
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseCleaner:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = create_client(self.url, self.key)

    def clean_duplicates(self, table_name):
        logger.info(f"--- {table_name} 테이블 중복 제거 시작 ---")
        
        # 1. 모든 데이터 가져오기 (데이터가 아주 많으면 분할해서 가져와야 함)
        # 여기서는 최근 데이터 위주로 중복이 발생했을 것이므로 전체 쿼리 시도
        response = self.client.table(table_name).select("*").execute()
        rows = response.data
        
        if not rows:
            logger.info("데이터가 없습니다.")
            return

        # 2. 내용/작성자/비디오ID 조합으로 그룹화
        groups = defaultdict(list)
        for row in rows:
            # 해시 키 생성 (내용, 작성자, 비디오ID)
            key = (row['author'], row['content'], row['video_id'])
            groups[key].append(row)

        to_delete_ids = []
        
        for key, members in groups.items():
            if len(members) > 1:
                # 중복 발생! 
                # 전략: '&'이 들어간 ID를 우선적으로 유지 (기존 방식)
                # 만약 둘 다 없거나 둘 다 있으면 가장 먼저 생성된 것을 유지하거나 
                # 더 긴 ID를 가진 것을 유지
                
                # 정렬 기준: 
                # 1순위: ID에 '&' 포함 여부
                # 2순위: ID 길이 (길수록 기존 데이터일 가능성 높음)
                sorted_members = sorted(
                    members, 
                    key=lambda x: ('&' in str(x['comment_id']), len(str(x['comment_id']))),
                    reverse=True
                )
                
                keep_node = sorted_members[0]
                redundant_nodes = sorted_members[1:]
                
                for node in redundant_nodes:
                    to_delete_ids.append(node['comment_id'])
                    logger.info(f"삭제 대상 발견: {node['comment_id']} (유지: {keep_node['comment_id']})")

        # 3. 삭제 실행
        if to_delete_ids:
            logger.info(f"총 {len(to_delete_ids)}개의 중복 데이터를 삭제합니다.")
            # Supabase API 제한 때문에 나눠서 삭제할 수도 있음
            for i in range(0, len(to_delete_ids), 100):
                chunk = to_delete_ids[i:i+100]
                self.client.table(table_name).delete().in_("comment_id", chunk).execute()
            logger.info("삭제 완료.")
        else:
            logger.info("중복 데이터가 없습니다.")

if __name__ == "__main__":
    cleaner = SupabaseCleaner()
    # 두 테이블 모두 체크
    cleaner.clean_duplicates("im_sung_gen_youtube_comments")
    cleaner.clean_duplicates("baek_jongwon_youtube_comments")
