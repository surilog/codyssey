import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AI_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://copa.codyssey.kr/v1/models", headers=headers)
print(response.json())