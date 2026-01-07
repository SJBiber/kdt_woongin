from supabase import create_client, Client
from configs.settings import settings

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def save_trending_snapshots(self, snapshots: list):
        """인기 급상승 영상 스냅샷을 저장합니다."""
        if not snapshots: return
        self.supabase.table("trending_snapshots").insert(snapshots).execute()

    def save_trend_analysis(self, analysis_data: list):
        """키워드 스냅샷 분석 결과를 저장합니다."""
        if not analysis_data: return
        self.supabase.table("trend_analysis").insert(analysis_data).execute()

    def save_viral_alert(self, alert_data: dict):
        """바이럴 알림 로그를 저장합니다."""
        self.supabase.table("viral_alerts").insert(alert_data).execute()
