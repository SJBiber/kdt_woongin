import httpx
from configs.settings import settings

class Notifier:
    async def send_alert(self, title: str, description: str, data: dict = None):
        if not settings.WEBHOOK_URL:
            print(f"[LOG] {title}: {description} | Data: {data}")
            return

        payload = {
            "content": f"## 🚨 {title}\n**{description}**",
            "embeds": [{
                "title": "Detailed Data",
                "color": 15158332,
                "fields": [{"name": k, "value": str(v), "inline": True} for k, v in (data or {}).items()]
            }]
        }

        async with httpx.AsyncClient() as client:
            await client.post(settings.WEBHOOK_URL, json=payload)
