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
        raise NotImplementedError("Please install pyaudio (sudo apt install python3-pyaudio) for best results.")

# 🔌 HARDWARE CONTROL STUB
class HardwareController:
    """Interface for Arduino/ESP32 (Future Integration)"""
    def __init__(self):
        self.connected = False
        self.serial = None
        # try:
        #     import serial
        #     self.serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        #     self.connected = True
        #     print("🔌 Hardware Controller Connected!")
        # except:
        #     print("🔌 Hardware Connect Failed (Mode: Software Only)")

    def send_command(self, cmd):
        if self.connected and self.serial:
            try:
                self.serial.write(f"{cmd}\n".encode())
            except:
                pass

class InteractiveGamingPartner:
    """Parthasarathi - Dual-Brain AI Partner (Vision + High IQ Logic)"""
    
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        
        # 🧠 DUAL BRAIN CONFIGURATION
        self.vision_model = "llava-phi3"       # The Eyes (Fast, Accurate Vision)
        self.thinking_model = "Parthasarathi-Mind" # The Mind (Baked-in Identity)
        
        # Identity
        self.name = "Parthasarathi"
        self.creator = "Dipesh Patel"
        
        # Hardware (Safe Init)
        try:
            self.hardware = HardwareController()
        except Exception as e:
            print(f"⚠️ Hardware Module Error: {e}")
            self.hardware = None
        
        # Vision Tools
        self.image_processor = AdvancedImageProcessor()
        self.scene_analyzer = GameplaySceneAnalyzer()
        self.cap = None 
        self.use_camera = True
        
        # Audio
        self.tts_voice = "hi-IN-SwaraNeural"
        self.recognizer = sr.Recognizer()
        
        # Hardware Check: Mic
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
        except Exception as e:
            print(f"⚠️ Microphone issue: {e}")
            self.mic_available = False
            self.mic = None
        
        # Memory & State
        self.conversation_history = []
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.last_observation_time = time.time()
        self.observation_interval = 25  # Slower interval for deeper thinking
        
        # Storage Paths
        self.base_dir = Path("/var/www/html/dipesh/Portfolio/live-Commentry")
        self.logger_dir = self.base_dir / "training_data" / "gold_dataset"
        self.memory_file = self.base_dir / "config" / "personal_memory.json"
        
        self.logger_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.personal_memory = self._load_memory()
        
        # Initialize Audio Output
        if PYGAME_AVAILABLE:
            try: pygame.mixer.init()
            except: pass

        print(f"✨ {self.name} is waking up...")
        print(f"👁️  Eyes: {self.vision_model}")
        print(f"🧠 Mind: {self.thinking_model}")
        print(f"👨‍💻 Creator: {self.creator}")
        
        self._init_camera()
        
    def _init_camera(self):
        """Initialize webcam if available"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("⚠️ Camera not found. Proceeding with Screen Only mode.")
                self.use_camera = False
            else:
                print("✅ Camera initialized.")
        except Exception as e:
            self.use_camera = False

    def _load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f: return json.load(f)
            except: pass
        return {"user_name": "Dipesh", "interests": [], "interactions_count": 0}

    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.personal_memory, f, indent=4)

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

    async def _get_visual_description(self, img_b64):
        """Step 1: The EYES analyze the scene"""
        # We ask the Vision Model for a pure factual description
        # It doesn't need to have personality, just accuracy.
        prompt = "Describe this gameplay scene in detail. Mention UI numbers (Health, Ammo), current action, and environment. Be factual."
        
        try:
            response = requests.post(f"{self.ollama_base_url}/api/generate", json={
                "model": self.vision_model,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False,
                "options": {"num_predict": 100, "temperature": 0.2} # Low temp for accuracy
            }, timeout=20)
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
        except:
            return "Visual analysis failed."
        return "No visual data."

    async def _get_strategic_response(self, visual_context, user_speech):
        """Step 2: The MIND thinks and replies"""
        # This uses the High-IQ Phi-4 Model
        user_name = self.personal_memory.get('user_name', 'Dipesh')
        
        system_prompt = f"""You are Parthasarathi, a brilliant AI Gaming Partner created by Dipesh Patel.

ROLE:
You are not an assistant. You are a "Sarthi" (Strategic Guide) and a "Dost" (Friend).
You are sitting next to {user_name} watching him play.

INPUT DATA:
1. SCREEN: {visual_context}
2. USER SAID: {user_speech if user_speech else "[User is silent]"}

INSTRUCTIONS:
1. THINK (Hidden): Analyze the game state. Is he winning? Losing? Need a tip? Or just a joke?
2. SPEAK (Hinglish): Generate a short response mixing Hindi and English naturally.
   - Good: "Arre bhai, health dekh apni! Peeche se enemy aa raha hai!"
   - Good: "Kya shot mara yaar! OP gameplay!"
   - Bad (Too formal): "Sir, your health is low. Please be careful."

FORMAT:
Thought: [Internal Strategy]
Response: [Hinglish Speech]"""

        try:
            response = requests.post(f"{self.ollama_base_url}/api/generate", json={
                "model": self.thinking_model,
                "prompt": system_prompt, 
                "stream": False,
                "options": {
                    "temperature": 0.9, # Higher creativity for Hinglish
                    "num_ctx": 4096,
                    "num_predict": 100
                }
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                if "Response:" in result:
                    return result.split("Response:")[1].strip(), result.split("Response:")[0]
                return result, "No thought generated"
        except Exception as e:
            print(f"Mind Error: {e}")
            return None, None
            
        return None, None

    async def generate_response(self, user_speech=None, proactive=False):
        """Execute the Dual-Brain Pipeline"""
        try:
            # 1. Capture Image
            vision_data = await self.capture_vision_safe()
            combined_img = self.prepare_multimodal_input(vision_data)
            processed_img = self.image_processor.preprocess_for_vision_model(combined_img)
            img_b64 = self.image_processor.to_base64(processed_img)
            
            # 2. Get Visual Facts (The Eyes)
            print("👁️  Analyze...")
            visual_facts = await self._get_visual_description(img_b64)
            # print(f"   Context: {visual_facts[:50]}...") # Debug
            
            # 3. Get Intelligent Reply (The Mind)
            print("🧠 Thinking...")
            reply, thought = await self._get_strategic_response(visual_facts, user_speech)
            
            if reply:
                # Log Data
                self._save_memory() # Update counts
                self._log_interaction(vision_data, user_speech or "[PROACTIVE]", f"Thought: {thought} | Visual: {visual_facts} | Reply: {reply}")
                
                # Update Context
                self.conversation_history.append(f"Parthasarathi: {reply}")
                if len(self.conversation_history) > 10: self.conversation_history.pop(0)
                
                return reply
                
            return None
            
        except Exception as e:
            print(f"❌ Pipeline Error: {e}")
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
