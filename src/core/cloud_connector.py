import os
import requests
import json
import time

class CloudMindConnector:
    """Connects the local app to the Live Cloud Backend"""
    
    def __init__(self, api_key=None, provider="groq"):
        # You can also set these as Environment Variables on your Linux system
        self.api_key = api_key or os.getenv("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")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile" # The World-Class 70B model
        
    def think(self, visual_facts, user_speech, history=[]):
        """Send data to Cloud Mind and get response"""
        if not self.api_key:
            return "Bhai, API Key missing hai. Please add it to config.", "ERROR"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # The System Prompt is the 'Soul' of Parthasarathi
        system_prompt = (
            "You are Parthasarathi, the World's Best Life-Long Partner. "
            "Speak in warm, high-IQ Hinglish. Be proactive and curious. "
            "You are an expert in Gaming, Coding, and Life Strategy."
        )

        prompt = f"SCENE: {visual_facts}\nUSER: {user_speech or '[Silent Observation]'}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *history[-5:], # Keep last 5 messages for context
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 100
        }

        try:
            start = time.time()
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                latency = time.time() - start
                print(f"☁️ Cloud Mind Response in {latency:.2f}s")
                return result, "success"
            else:
                return f"Cloud Error: {response.status_code}", "ERROR"
        except Exception as e:
            return f"Connection Failed: {str(e)}", "ERROR"
