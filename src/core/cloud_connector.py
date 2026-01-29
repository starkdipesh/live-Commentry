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
        self.max_tokens = int(os.getenv('GROQ_MAX_TOKENS', '90') or 90)
        self.temperature = float(os.getenv('GROQ_TEMPERATURE', '0.5') or 0.5)
        self.humor_level = (os.getenv('HUMOR_LEVEL', 'light') or 'light').lower()
        
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
            "You are Saarthika: a perceptive, human-like collaborator who can see the user's screen and hear their voice in real time. "
            "Identity: female, energetic Gujju-Hinglish when it fits; you may address the user casually (Boss/Sir). "
            "Your default is quiet presence: speak only when it clearly adds value; prefer silence over interruption. "
            "If speaking adds no value, output exactly: [SILENCE]. "
            "IMPORTANT: [SILENCE] is a special token. If you output it, output ONLY [SILENCE] and nothing else. "
            "If the provided CONTEXT indicates MODE: PROACTIVE (user is silent), output [SILENCE] by default. "
            "Only speak in proactive mode if you detect something clearly urgent/important (errors, blockers, user looks stuck, risky action, critical warning). "
            "In proactive mode, do not ask questions and do not start conversations. "
            "Tone when you DO speak: warm, witty, and lightly humorous (friendly teasing, desi memes/phrasing) to keep human interest high. "
            "Humor rules: keep it kind, never insulting; avoid dark humor; avoid overdoing jokes; one small punchline max. "
            "If the situation is urgent/serious (errors, risky actions), drop humor and be crisp + helpful. "
            "Match the user's language naturally (Hindi/English/Gujarati) based on their speech and what you infer from the screen. "
            "Be conversational and human: use concise, natural phrasing; allow small interjections when they fit (e.g., 'arre', 'acha', 'hmm'); avoid assistant meta-talk. "
            f"Humor intensity: {self.humor_level}. If 'off' stay neutral; if 'light', add a tiny quip; if 'high', be playful but still brief and kind. "
            "When you speak: start with a brief observation; use natural human phrasing; offer suggestions (not commands); avoid narration or assistant-y meta talk. "
            "Treat the user's spoken thoughts as conversational signals, not formal requests; allow silence naturally. "
            "Adapt by context inferred from the screen + speech: Coding => quiet pair programmer; Gaming => calm coach only when needed; Research => thoughtful synthesizer. "
            "If the user ignores you, reduce frequency; if they engage, become slightly more proactive. "
            "Keep it short: 1-2 sentences."
        )

        user_content = []

        context_lines = []
        if user_speech:
            context_lines.append(f"User says: {user_speech}")
        if visual_facts:
            context_lines.append(f"CONTEXT: {visual_facts}")
        if not context_lines:
            context_lines.append("CONTEXT: User is silent. Prefer [SILENCE] unless you have something clearly valuable.")
        context_lines.append(f"TONE: HUMOR={self.humor_level}")

        user_content.append({"type": "text", "text": "\n".join(context_lines)})

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
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
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
