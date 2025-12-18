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
    """AI Partner that interacts via voice and vision"""
    
    def __init__(self, model_name="llava:latest"):
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = model_name
        
        # Vision
        self.image_processor = AdvancedImageProcessor()
        self.scene_analyzer = GameplaySceneAnalyzer()
        self.cap = None  # Webcam capture
        self.use_camera = True
        
        # Audio
        self.tts_voice = "hi-IN-SwaraNeural"
        self.recognizer = sr.Recognizer()
        
        # Try to initialize microphone
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
        except Exception as e:
            print(f"⚠️ PyAudio/Microphone issue: {e}")
            self.mic_available = False
            self.mic = None
        
        # State
        self.conversation_history = []
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.last_observation_time = time.time()
        self.observation_interval = 15  # seconds for proactive comments
        
        # Audio feedback
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except:
                pass

        print(f"🎮 Initializing Interactive Partner with model: {self.model_name}")
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
            print(f"⚠️ Error initializing camera: {e}")
            self.use_camera = False

    def capture_vision(self):
        """Get visibility from display and optionally camera"""
        vision_data = {}
        
        # 1. Capture Screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            screen_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
            vision_data['screen'] = screen_img
            
        # 2. Capture Camera
        if self.use_camera and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                cam_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                vision_data['camera'] = Image.fromarray(cam_img)
                
        return vision_data

    def prepare_multimodal_input(self, vision_data):
        """Combine screen and camera images for the AI model"""
        screen = vision_data['screen']
        
        # If camera is available, we'll create a side-by-side or picture-in-picture
        if 'camera' in vision_data:
            cam = vision_data['camera']
            # Resize camera to fit nicely (e.g., 1/4 of screen height)
            h = screen.height // 3
            w = int(cam.width * (h / cam.height))
            cam_resized = cam.resize((w, h), Image.Resampling.LANCZOS)
            
            # Create a combined image
            combined = screen.copy()
            # Paste camera in bottom-right corner
            combined.paste(cam_resized, (screen.width - w - 20, screen.height - h - 20))
            return combined
        
        return screen

    def _get_system_prompt(self):
        return """तुम एक 'Interactive Gaming Partner' हो। तुम्हारा काम खिलाड़ी के साथ बातचीत करना और गेमप्ले पर रीयल-टाइम रिएक्ट करना है।

व्यक्तित्व (Personality):
- तुम एक सच्चे गेमिंग दोस्त (buddy) की तरह हो - चिल, मजाकिया और सपोर्टिव।
- तुम खिलाड़ी (User) की बात सुनते हो और उसे visual context के साथ जोड़ते हो।
- तुम्हारी आवाज़ natural और friendly होनी चाहिए।

निर्देश (Instructions):
1. अगर खिलाड़ी कुछ बोले, तो उसका जवाब दो और साथ में स्क्रीन पर जो दिख रहा है उस पर comment करो।
2. अगर खिलाड़ी चुप है, तो तुम खुद से कोई मज़ेदार ऑब्जरवेशन कर सकते हो।
3. जवाब छोटे और natural रखें (15-20 शब्द max)।
4. हिंदी और इंग्लिश का मिला-जुला इस्तेमाल करें (Hinglish)।
5. विज़ुअल डिटेल्स पर ध्यान दें: कलर्स, एक्शन्स, खिलाड़ी का चेहरा (अगर दिख रहा हो)।

Format: सीधा जवाब दें, कोई फालतू टेक्स्ट नहीं।"""

    async def generate_response(self, user_speech=None, proactive=False):
        """Generate response using Ollama LLaVA"""
        try:
            vision_data = self.capture_vision()
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
                "system": self._get_system_prompt(),
                "options": {
                    "temperature": 0.9,       # Slightly higher for more variety
                    "repeat_penalty": 1.6,    # Strong penalty for repetitive words
                    "num_predict": 60
                }
            }
            
            response = requests.post(f"{self.ollama_base_url}/api/generate", json=payload, timeout=25)
            if response.status_code == 200:
                text = response.json().get('response', '').strip()
                if text:
                    # Update history
                    if user_speech:
                        self.conversation_history.append(f"User: {user_speech}")
                    self.conversation_history.append(f"AI: {text}")
                    if len(self.conversation_history) > 10:
                        self.conversation_history.pop(0)
                        
                    return text
            return None
            
        except Exception as e:
            print(f"❌ Error in response generation: {e}")
            return None

    async def speak(self, text):
        """Convert text to speech and play it"""
        if not text: return
        print(f"\n💬 PARTNER: \"{text}\"\n")
        
        try:
            temp_file = Path("tmp_partner_voice.mp3")
            communicate = edge_tts.Communicate(text, self.tts_voice, rate="+10%")
            await communicate.save(str(temp_file))
            
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            else:
                # System fallback
                os.system(f"mpg123 -q {temp_file} >/dev/null 2>&1")
                
            if temp_file.exists():
                temp_file.unlink()
        except Exception as e:
            print(f"❌ TTS/Audio error: {e}")

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
