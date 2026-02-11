from google import genai
import os
from dotenv import load_dotenv

# .envファイルをロード
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY is not set in .env")
else:
    client = genai.Client(api_key=api_key)
    print("Listing available Gemini models:")
    try:
        for m in client.models.list():
            # 新SDKではsupported_generation_methodsの属性名や構造が異なる可能性があるが、
            # 基本的なリストアップを行う
            print(f"- {m.name}: {m.display_name}")
    except Exception as e:
        print(f"Error listing models: {e}")
