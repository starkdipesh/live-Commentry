import os
import requests
import json
import time

class CloudMindConnector:
    """Connects the local app to the Live Cloud Backend"""
    
    def __init__(self, api_key=None, provider="groq"):
        # You can also set these as Environment Variables on your Linux system
        self.api_key = api_key or ""
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct" # Best vision model for multi-modal requirements
        
    def think(self, visual_facts, user_speech, history=[], image_b64=None):
        """Send data to Cloud Mind and get response (supports Vision)"""
        if not self.api_key:
            return "Bhai, API Key missing hai. Please add it to config.", "ERROR"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # The System Prompt is the 'Soul' of Parthasarathi
        system_prompt = (
            "You are Parthasarathi, the World's Best Life-Long Partner. "
            "Soul: Talk in STRICT HINGLISH. Edgier, smarter, and proactive. "
            "You are an expert in Gaming, Coding, and Life Strategy. "
            "Instruction: Speak like a human partner. Max 20 words. Mix Hindi/English naturally. "
            "Boss Mode: Address user as 'Boss' or 'Sir'."
        )

        user_content = []
        if user_speech:
             user_content.append({"type": "text", "text": f"User says: {user_speech}"})
        
        if image_b64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
        else:
            user_content.append({"type": "text", "text": f"SCENE DESCRIPTION: {visual_facts or 'Offline interaction'}"})

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *history[-5:], 
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.8,
            "max_tokens": 150
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
