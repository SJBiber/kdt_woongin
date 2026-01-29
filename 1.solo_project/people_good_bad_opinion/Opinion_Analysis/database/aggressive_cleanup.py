import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from collections import defaultdict

# .env 로드
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseAggressiveCleaner:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = create_client(self.url, self.key)

    def fetch_all_rows(self, table_name):
        all_rows = []
        offset = 0
        limit = 1000
        
        while True:
            response = self.client.table(table_name).select("*").range(offset, offset + limit - 1).execute()
            rows = response.data
            if not rows:
                break
            all_rows.extend(rows)
            offset += limit
            logger.info(f"{table_name}: {len(all_rows)} rows fetched...")
        return all_rows

    def clean_duplicates(self, table_name):
        logger.info(f"--- {table_name} 테이블 중복 제거 (추종 모드) 시작 ---")
        
        rows = self.fetch_all_rows(table_name)
        if not rows: return

        # 그룹화: (작성자, 정규화된 내용)
        groups = defaultdict(list)
        for row in rows:
            # 특수문자/공백 모두 제거하여 내용 일치 확인 자가진단
            clean_content = re.sub(r'\W+', '', str(row['content']))
            author = str(row['author']).strip()
            key = (author, clean_content)
            groups[key].append(row)

        to_delete_ids = []
        
        for key, members in groups.items():
            if len(members) > 1:
                # 중복 데이터 중 하나만 남기기 위한 우선순위 정렬
                sorted_members = sorted(
                    members, 
                    key=lambda x: (
                        # 1순위: hash_가 아닌 진짜 ID를 선호함 (False가 True보다 앞에 옴)
                        not str(x['comment_id']).startswith('hash_'),
                        # 2순위: 특수문자(&)가 포함된 상세 ID 선호
                        '&' in str(x['comment_id']),
                        # 3순위: 날짜 정보가 있는 것 선호
                        x.get('published_at') is not None,
                        # 4순위: ID의 길이
                        len(str(x['comment_id']))
                    ),
                    reverse=True
                )
                
                keep_node = sorted_members[0]
                redundant_nodes = sorted_members[1:]
                
                for node in redundant_nodes:
                    to_delete_ids.append(node['comment_id'])
                    logger.info(f"삭제 확정: {node['comment_id']} (유지: {keep_node['comment_id']}, 이유: 실제 ID 우선)")

        if to_delete_ids:
            logger.info(f"총 {len(to_delete_ids)}개의 중복 데이터를 제거합니다.")
            for i in range(0, len(to_delete_ids), 100):
                chunk = to_delete_ids[i:i+100]
                self.client.table(table_name).delete().in_("comment_id", chunk).execute()
            logger.info("정리 완료.")
        else:
            logger.info("중복 데이터가 발견되지 않았습니다.")

if __name__ == "__main__":
    cleaner = SupabaseAggressiveCleaner()
    cleaner.clean_duplicates("im_sung_gen_youtube_comments")
    cleaner.clean_duplicates("baek_jongwon_youtube_comments")
