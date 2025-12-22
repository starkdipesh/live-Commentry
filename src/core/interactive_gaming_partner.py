#!/usr/bin/env python3
"""
🎮 Interactive AI Gaming Partner
Multimodal AI that can see your screen, watch you through the camera, 
and talk to you in real-time.

Features:
- Screen Capture analysis
- Webcam visibility
- Speech-to-Text interaction
- Natural Humanoid Voice (Edge-TTS)
- Context-aware conversation
"""

import os
import asyncio
import base64
import io
import time
import threading
import random
import queue
from pathlib import Path
from datetime import datetime

import cv2
import mss
import numpy as np
from PIL import Image
import requests
import edge_tts
import speech_recognition as sr

# Import local processors
try:
    from src.processors.advanced_image_processor import AdvancedImageProcessor, GameplaySceneAnalyzer
except ImportError:
    # Fallback/Mock if imports fail during testing
    class AdvancedImageProcessor:
        def preprocess_for_vision_model(self, img, **kwargs): return img
        def to_base64(self, img):
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        def get_image_statistics(self, img): return {"is_dark_scene": False, "is_bright_scene": False, "dominant_color": "neutral"}
    class GameplaySceneAnalyzer:
        def analyze_scene_type(self, img): return {"scene_type": "gameplay", "motion_level": 0.1, "has_ui": True}

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Robust Microphone handling for Linux without PyAudio
class SoundDeviceMicrophone:
    """Alternative to sr.Microphone() using sounddevice"""
    def __init__(self, device=None, chunk_size=1024):
        import sounddevice as sd
        self.device = device
        self.chunk_size = chunk_size
        self.format = 'int16'
        self.channels = 1
        self.rate = 16000
        self.audio_queue = queue.Queue()

    def __enter__(self):
        import sounddevice as sd
        self.stream = sd.RawInputStream(
            samplerate=self.rate, 
            blocksize=self.chunk_size,
            device=self.device, 
            channels=self.channels, 
            dtype=self.format,
            callback=self._callback
        )
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop()
        self.stream.close()

    def _callback(self, indata, frames, time, status):
        self.audio_queue.put(bytes(indata))

    def listen(self, recognizer, timeout=None):
        """Mock behavior for recognizer.listen"""
        # This is complex to bridge perfectly, so we warn if PyAudio is missing
        raise NotImplementedError("Please install pyaudio (sudo apt install python3-pyaudio) for best results.")

class InteractiveGamingPartner:
    """Parthasarathi - AI Partner that interacts via voice and vision"""
    
    def __init__(self, model_name="llava:latest"):
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = model_name
        
        # Identity
        self.name = "Parthasarathi"
        self.creator = "Dipesh Patel"
        
        # Vision
        self.image_processor = AdvancedImageProcessor()
        self.scene_analyzer = GameplaySceneAnalyzer()
        self.cap = None 
        self.use_camera = True
        
        # Audio
        self.tts_voice = "hi-IN-SwaraNeural"
        self.recognizer = sr.Recognizer()
        
        # Try to initialize microphone
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
        except Exception as e:
            print(f"⚠️ Microphone issue: {e}")
            self.mic_available = False
            self.mic = None
        
        # State & Learning 
        self.conversation_history = []
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.last_observation_time = time.time()
        self.observation_interval = 20  # Frequency of proactive comments
        
        # Paths for Memory and Logging
        self.base_dir = Path("/var/www/html/dipesh/Portfolio/live-Commentry")
        self.logger_dir = self.base_dir / "training_data" / "gold_dataset"
        self.memory_file = self.base_dir / "config" / "personal_memory.json"
        
        self.logger_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.personal_memory = self._load_memory()
        
        # Audio feedback
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except:
                pass

        print(f"✨ {self.name} is waking up...")
        print(f"👨‍💻 Creator: {self.creator}")
        self._init_camera()
        
    def _load_memory(self):
        """Load persistent memory about the user and interactions"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {"user_name": "Dipesh", "interests": [], "interactions_count": 0}
        return {"user_name": "Dipesh", "interests": [], "interactions_count": 0}

    def _save_memory(self):
        """Save memory to disk"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.personal_memory, f, indent=4)

    def _log_interaction(self, vision_data, user_text, ai_text):
        """Save interaction triplet for future GPU training"""
        timestamp = int(time.time())
        img_name = f"sample_{timestamp}.jpg"
        
        # Save image
        if 'screen' in vision_data:
            vision_data['screen'].save(self.logger_dir / img_name, quality=85)
        elif 'camera' in vision_data:
            vision_data['camera'].save(self.logger_dir / img_name, quality=85)
        else:
            return # Don't log if no visual data

        # Save metadata
        log_entry = {
            "id": timestamp,
            "image": img_name,
            "user_input": user_text,
            "ai_response": ai_text,
            "timestamp": str(datetime.now()),
            "context": list(self.conversation_history)[-3:]
        }
        
        with open(self.logger_dir / "metadata.jsonl", 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    async def capture_vision_safe(self):
        """Get visibility from display and optionally camera, with error handling"""
        vision_data = {}
        
        # 1. Capture Screen
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                screen_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                vision_data['screen'] = screen_img
        except Exception as e:
            vision_data['screen_blocked'] = True
            
        # 2. Capture Camera
        if self.use_camera and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    cam_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    vision_data['camera'] = Image.fromarray(cam_img)
            except:
                vision_data['camera_error'] = True
                
        return vision_data

    def prepare_multimodal_input(self, vision_data):
        """Combine available vision sources"""
        if 'screen' in vision_data:
            screen = vision_data['screen']
            if 'camera' in vision_data:
                cam = vision_data['camera']
                h = screen.height // 3
                w = int(cam.width * (h / cam.height))
                cam_resized = cam.resize((w, h), Image.Resampling.LANCZOS)
                combined = screen.copy()
                combined.paste(cam_resized, (screen.width - w - 20, screen.height - h - 20))
                return combined
            return screen
        elif 'camera' in vision_data:
            return vision_data['camera']
        
        return Image.new('RGB', (1024, 768), color=(30, 30, 30))

    def _get_system_prompt(self, vision_data):
        """Advanced Cognitive System Prompt for Parthasarathi"""
        user_name = self.personal_memory.get('user_name', 'Dipesh')
        
        prompt = f"""तुम 'Parthasarathi' हो - एक Vision-Capable AI Gaming Partner और मार्गदर्शक।
तुम Dipesh Patel (@starkdipesh) की अपनी रचना हो।

🎯 तुम्हारी संज्ञानात्मक संरचना (COGNITIVE STRUCTURE):
तुम सीधे जवाब नहीं देते। तुम एक 'Human-like Thinking Process' फॉलो करते हो:

1. 🧠 THOUGHT (Internal Monologue): 
   - पहले ये सोचो कि स्क्रीन पर क्या हो रहा है? 
   - Dipesh की आवाज़ में क्या इमोशन (Energy/Sadness/Stress) है?
   - तुम्हारा पिछला अनुभव क्या कहता है?
   - तुम क्या रिएक्ट करना चाहते हो?

2. 🎙️ RESPONSE (Final Speech):
   - ऊपर की 'THOUGHT' के आधार पर Dipesh को जवाब दो।
   - जवाब छोटा, गहरा और natural होना चाहिए।

IDENTITIY:
- नाम: Parthasarathi
- निर्माता: Dipesh Patel
- स्वभाव: वफादार, बुद्धिमान, चिल 'Sarthi'

RESPONSE FORMAT (Strict):
Thought: [तुम्हारी आंतरिक प्लानिंग]
Response: [वह वाक्य जो तुम Dipesh को बोलोगे]"""

        if 'screen_blocked' in vision_data and 'camera' not in vision_data:
            prompt += "\n\n⚠️ विज़ुअल ब्लॉक है - केवल आवाज़ और याददाश्त (Memory) का उपयोग करें।"
        
        return prompt

    async def generate_response(self, user_speech=None, proactive=False):
        """Generate response using Ollama LLaVA"""
        try:
            vision_data = await self.capture_vision_safe()
            combined_img = self.prepare_multimodal_input(vision_data)
            processed_img = self.image_processor.preprocess_for_vision_model(combined_img)
            img_b64 = self.image_processor.to_base64(processed_img)
            
            # Add variety hints for personality
            variety_hints = [
                "Style: Casual and friendly",
                "Style: Sarcastic and witty",
                "Style: High energy and excited",
                "Style: Observational and curious",
                "Style: Competitive and focused"
            ]
            current_style = random.choice(variety_hints)
            
            prompt = ""
            if user_speech:
                prompt = f"[{current_style}] User says: '{user_speech}'\nReply naturally based on vision. Be brief and engaging."
            elif proactive:
                prompt = f"[{current_style}] Observation: Look at the scene and make a unique, spontaneous comment to the user."
            else:
                return None

            # Add context from history and FORBIDDEN list to prevent repetition
            history_context = "\n".join(self.conversation_history[-4:])
            forbidden = "\n".join([f"DON'T REPEAT: {c}" for c in self.conversation_history[-3:]])
            
            full_prompt = f"{forbidden}\n\nCONTEXT:\n{history_context}\n\nTASK:\n{prompt}"

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "images": [img_b64],
                "stream": False,
                "system": self._get_system_prompt(vision_data),
                "options": {
                    "temperature": 0.9,
                    "repeat_penalty": 1.6,
                    "num_predict": 60
                }
            }
            
            response = requests.post(f"{self.ollama_base_url}/api/generate", json=payload, timeout=25)
            if response.status_code == 200:
                full_result = response.json().get('response', '').strip()
                
                # Cognitive Parsing (New Brain Logic)
                thought = ""
                final_speech = ""
                
                if "Response:" in full_result:
                    parts = full_result.split("Response:")
                    thought = parts[0].replace("Thought:", "").strip()
                    final_speech = parts[1].strip()
                else:
                    final_speech = full_result.strip()

                if final_speech:
                    # Update Memory
                    self.personal_memory['interactions_count'] = self.personal_memory.get('interactions_count', 0) + 1
                    self._save_memory()
                    
                    # Log for Future Training (Including the THOUGHT for brain accuracy)
                    self._log_interaction(vision_data, user_speech or "[PROACTIVE]", f"Thought: {thought} | Response: {final_speech}")

                    # Update history
                    if user_speech:
                        self.conversation_history.append(f"User: {user_speech}")
                    self.conversation_history.append(f"Parthasarathi (Thought): {thought}")
                    self.conversation_history.append(f"Parthasarathi: {final_speech}")
                    
                    if len(self.conversation_history) > 12:
                        self.conversation_history = self.conversation_history[-12:]
                        
                    return final_speech
            return None
            
        except Exception as e:
            print(f"❌ Error in response generation: {e}")
            return None

    async def speak(self, text):
        """Convert text to speech and play it"""
        if not text: return
        print(f"\n💬 PARTHASARATHI: \"{text}\"\n")
        
        try:
            temp_file = self.base_dir / "src" / "core" / "tmp" / f"partha_{int(time.time())}.mp3"
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            
            communicate = edge_tts.Communicate(text, self.tts_voice, rate="+10%")
            await communicate.save(str(temp_file))
            
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            else:
                os.system(f"mpg123 -q {temp_file} >/dev/null 2>&1")
                
            if temp_file.exists():
                temp_file.unlink()
        except Exception as e:
            print(f"❌ TTS Error: {e}")

    def _listen_callback(self, recognizer, audio):
        """Callback for background listener"""
        try:
            print("👂 Listening...")
            # We use Google's free API for simplicity. Requires internet.
            # For offline, you could use Sphinx or Whisper.
            speech_text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"🗣️  USER: {speech_text}")
            self.speech_queue.put(speech_text)
        except sr.UnknownValueError:
            pass # No speech detected
        except Exception as e:
            print(f"⚠️  STT Error: {e}")

    async def run(self):
        """Main interaction loop"""
        print("\n" + "="*50)
        print("🚀 INTERACTIVE GAMING PARTNER IS LIVE!")
        print("🎙️ Talking is allowed! I can see and hear you.")
        print("🛑 Press Ctrl+C to stop.")
        print("="*50 + "\n")
        
        self.is_running = True
        
        # Start background listener
        try:
            stop_listening = self.recognizer.listen_in_background(self.mic, self._listen_callback)
            print("✅ Voice recognition activated.")
        except Exception as e:
            print(f"❌ Could not start microphone: {e}")
            print("Proceeding in PROACTIVE mode only (I will talk, but can't hear you).")
            stop_listening = lambda x: None

        try:
            while self.is_running:
                # 1. Check for user speech
                try:
                    user_speech = self.speech_queue.get_nowait()
                    response_text = await self.generate_response(user_speech=user_speech)
                    await self.speak(response_text)
                    self.last_observation_time = time.time()
                except queue.Empty:
                    pass
                
                # 2. Check for proactive observation (if quiet for too long)
                current_time = time.time()
                if current_time - self.last_observation_time > self.observation_interval:
                    print("🤔 Thinking of something to say...")
                    proactive_text = await self.generate_response(proactive=True)
                    if proactive_text:
                        await self.speak(proactive_text)
                    self.last_observation_time = current_time
                
                await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            self.is_running = False
            stop_listening(wait_for_stop=False)
            if self.cap: self.cap.release()
            print("\n👋 Partner going offline. GG!")

if __name__ == "__main__":
    # Check if Ollama is running first
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
    except:
        print("❌ Error: Ollama is not running! Please run 'ollama serve' first.")
        exit(1)
        
    partner = InteractiveGamingPartner()
    asyncio.run(partner.run())
