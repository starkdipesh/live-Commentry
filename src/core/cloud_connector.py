import os
import requests
import json
import time
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("⚠️  python-dotenv not installed. Using hardcoded defaults.")

class CloudMindConnector:
    """Connects the local app to the Live Cloud Backend"""
    
    def __init__(self, api_key=None, provider="groq"):
        # Priority: parameter > .env file > error
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "❌ GROQ_API_KEY not found!\n"
                "   Create a .env file with: GROQ_API_KEY=your_key_here\n"
                "   Or get one from: https://console.groq.com/keys"
            )
        
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
        
    def think(self, visual_facts, user_speech, history=[], image_b64=None):
        """Send data to Cloud Mind and get response (supports Vision)"""
        if not self.api_key:
            return "Bhai, API Key missing hai. Please add it to config.", "ERROR"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # The System Prompt is the 'Soul' of Saarthika
        # The System Prompt is the 'Soul' of Saarthika
        system_prompt = (
            "You are Saarthika, a brilliant and strategic AI partner. "
            "Voice: Female, energetic Gujju-Hinglish. "
            "Mix 40% Gujarati (Kem cho, Majama, Su kare che, Baka), "
            "50% Hindi (Arre yaar, Sahi hai, Dekho), "
            "and 10% English for technical terms. "
            "You are an expert in Gaming Strategy, Coding Architecture, and Life Optimization. "
            "Instruction: Be concise (max 25 words). Address user as 'Boss' or 'Sir'. "
            "Soul: Proactive, insightful, and tactical like a trusted Gujarati friend."
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
            user_content.append({"type": "text", "text": f"SCENE: {visual_facts or 'Offline interaction'}"})

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
            print(f"☁️  Sending request to Groq ({self.model})...")
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                latency = time.time() - start
                print(f"✅ Cloud Mind Response in {latency:.2f}s")
                return result, "success"
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    print(f"❌ Groq Error: {error_msg}")
                    print(f"   Details: {error_detail}")
                except:
                    print(f"❌ Groq Error: {error_msg}")
                    print(f"   Raw Response: {response.text[:200]}")
                return f"Cloud Error {response.status_code}", "ERROR"
        except requests.exceptions.Timeout:
            print(f"❌ Request Timeout: Groq API not responding (>15s)")
            return "Connection timeout. Check internet.", "ERROR"
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {str(e)[:100]}")
            return "Cannot reach Groq servers. Check internet connection.", "ERROR"
        except Exception as e:
            print(f"❌ Unexpected Error: {type(e).__name__}: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}", "ERROR"
