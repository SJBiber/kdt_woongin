from google import genai
from configs.settings import settings

def list_models():
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY is missing")
        return
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    for model in client.models.list():
        print(f"Model ID: {model.name}, Supported: {model.supported_actions}")

if __name__ == "__main__":
    list_models()
