import requests
import os

key = ""
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {key}"}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        print("Available Models:")
        for m in models:
            print(f"- {m['id']}")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Error: {e}")
