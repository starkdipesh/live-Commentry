#!/usr/bin/env python3
"""
🎮 Interactive AI Gaming Partner - DEBUG VERSION
This version has extensive logging to find where it's hanging
"""

import json
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
    class AdvancedImageProcessor:
        def preprocess_for_vision_model(self, img, **kwargs): 
            return img
        def to_base64(self, img):
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        def get_image_statistics(self, img): 
            return {"is_dark_scene": False, "is_bright_scene": False, "dominant_color": "neutral"}
    class GameplaySceneAnalyzer:
        def analyze_scene_type(self, img): 
            return {"scene_type": "gameplay", "motion_level": 0.1, "has_ui": True}

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class HardwareController:
    def __init__(self):
        self.connected = False
        self.serial = None

    def send_command(self, cmd):
        pass

class InteractiveGamingPartner:
    """Parthasarathi - Debug Version"""
    
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        
        # 🧠 DUAL BRAIN CONFIGURATION
        self.use_cloud_mind = False  # Set to True once you have an API key (Groq/HF)
        
        # Local Models (Eyes)
        self.vision_model = "llava-phi3"
        
        # Cloud Mind Config (The Genius Brain - Zero CPU Load)
        self.cloud_api_key = "YOUR_FREE_GROQ_OR_HF_KEY" 
        self.cloud_base_url = "https://api.groq.com/openai/v1" # Or any OpenAI-compatible provider
        self.thinking_model = "llama-3.3-70b-versatile" # 70B Model for FREE!
        
        # Identity
        self.name = "Parthasarathi"
        self.creator = "Dipesh Patel"
        
        # Hardware
        try:
            self.hardware = HardwareController()
        except Exception as e:
            print(f"⚠️ Hardware Module Error: {e}")
            self.hardware = None
        
        # Vision Tools (Turbo Optimized: 336px is native for llava-phi3)
        self.image_processor = AdvancedImageProcessor(enhance_mode='speed', target_size=336)
        self.scene_analyzer = GameplaySceneAnalyzer()
        self.cap = None 
        self.use_camera = True
        
        # Audio Configuration
        self.tts_voice = "hi-IN-SwaraNeural"
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        # Hardware Check: Mic
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
            print("✅ Microphone detected")
        except Exception as e:
            print(f"⚠️ Microphone issue: {e}")
            self.mic_available = False
            self.mic = None
        
        # Memory & State
        self.conversation_history = []
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.last_observation_time = time.time()
        self.observation_interval = 45  # Increased for CPU efficiency
        self.last_visual_context = ""
        
        # Storage Paths
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.logger_dir = self.base_dir / "training_data" / "gold_dataset"
        self.memory_file = self.base_dir / "config" / "personal_memory.json"
        
        self.logger_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.personal_memory = self._load_memory()
        
        # Initialize Audio Output
        if PYGAME_AVAILABLE:
            try: 
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ Audio output initialized")
            except Exception as e:
                print(f"⚠️ Audio init warning: {e}")

        print(f"\n{'='*60}")
        print(f"✨ {self.name} is waking up...")
        print(f"👁️  Eyes: {self.vision_model}")
        print(f"🧠 Mind: {self.thinking_model}")
        print(f"👨‍💻 Creator: {self.creator}")
        
        # Check for Wayland (Ubuntu)
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            print("\n⚠️  WARNING: You are running Ubuntu on Wayland.")
            print("   Screen capture might return a black screen.")
            print("   If it fails, switch to 'Ubuntu on Xorg' at the login screen.\n")
            
        print(f"{'='*60}\n")
        
        self._init_camera()
        self._verify_models()
        
    def _verify_models(self):
        """Check if required models are available"""
        try:
            print("🔍 Verifying models...")
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                print(f"   Available: {models}")
                
                vision_ok = any(self.vision_model in m for m in models)
                thinking_ok = any(self.thinking_model in m for m in models)
                
                if not vision_ok:
                    print(f"❌ Vision model '{self.vision_model}' not found!")
                if not thinking_ok:
                    print(f"❌ Thinking model '{self.thinking_model}' not found!")
                    
                if vision_ok and thinking_ok:
                    print(f"✅ All models verified!")
            else:
                print(f"⚠️  Could not verify models (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️  Model verification failed: {e}")
        
    def _init_camera(self):
        """Initialize webcam if available"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("⚠️ Camera not found. Screen Only mode.")
                self.use_camera = False
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                print("✅ Camera initialized (640x480)")
        except Exception as e:
            print(f"⚠️ Camera initialization failed: {e}")
            self.use_camera = False

    def _load_memory(self):
        """Load persistent memory from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Memory load error: {e}")
        return {
            "user_name": "Dipesh", 
            "interests": [], 
            "interactions_count": 0,
            "favorite_games": [],
            "last_session": None
        }

    def _save_memory(self):
        """Save persistent memory to disk"""
        try:
            self.personal_memory['last_session'] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.personal_memory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Memory save error: {e}")

    def _log_interaction(self, final_image, user_input, full_context):
        """Log interaction and save final processed image for the Gold Dataset"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. Save JSON Log
            log_file = self.logger_dir / f"log_{timestamp}.json"
            log_data = {
                "timestamp": timestamp,
                "user_input": user_input,
                "context": full_context,
                "session_id": self.personal_memory.get('last_session', 'unknown')
            }
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            # 2. Save the exact image the AI saw (Turbo 336px)
            img_path = self.logger_dir / f"frame_{timestamp}.jpg"
            final_image.save(img_path, quality=85)
                
            print(f"💾 Interaction learned and saved to Gold Dataset.")
                
        except Exception as e:
            print(f"⚠️ Logger Error: {e}")

    async def capture_vision_safe(self):
        """Get visibility from display and optionally camera"""
        print("   [1] Capturing vision...")
        vision_data = {}
        
        # 1. Capture Screen
        try:
            print("      - Grabbing screen...")
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                screen_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                vision_data['screen'] = screen_img
                print("      ✓ Screen captured")
        except Exception as e:
            print(f"      ✗ Screen capture failed: {e}")
            vision_data['screen_blocked'] = True
            
        # 2. Capture Camera (if enabled)
        if self.use_camera and self.cap:
            try:
                print("      - Grabbing camera...")
                ret, frame = self.cap.read()
                if ret:
                    cam_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    vision_data['camera'] = Image.fromarray(cam_img)
                    print("      ✓ Camera captured")
            except Exception as e:
                print(f"      ✗ Camera capture failed: {e}")
                vision_data['camera_error'] = True
                
        return vision_data

    def prepare_multimodal_input(self, vision_data):
        """Combine available vision sources"""
        print("   [2] Preparing image...")
        if 'screen' in vision_data:
            screen = vision_data['screen']
            
            if 'camera' in vision_data:
                cam = vision_data['camera']
                h = screen.height // 3
                w = int(cam.width * (h / cam.height))
                cam_resized = cam.resize((w, h), Image.Resampling.LANCZOS)
                
                combined = screen.copy()
                combined.paste(cam_resized, (screen.width - w - 20, screen.height - h - 20))
                print("      ✓ Combined screen + camera")
                return combined
            print("      ✓ Using screen only")
            return screen
            
        elif 'camera' in vision_data:
            print("      ✓ Using camera only")
            return vision_data['camera']
        
        print("      ✓ Using black fallback")
        return Image.new('RGB', (1024, 768), color=(30, 30, 30))

    async def _get_visual_description(self, img_b64):
        """Step 1: Vision Model Analysis"""
        print("   [3] Calling VISION model...")
        
        prompt = "Describe what you see in 1-2 sentences. Mention any UI, actions, or environment."
        
        try:
            start_time = time.time()
            print(f"      - Sending request to {self.vision_model}...")
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate", 
                json={
                    "model": self.vision_model,
                    "prompt": prompt,
                    "images": [img_b64],
                    "stream": False,
                    "options": {
                        "num_predict": 30,  # Ultra-fast punchy description
                        "temperature": 0.1,
                        "num_thread": 8     # Assuming 8 threads, Ollama will optimize
                    },
                    "keep_alive": "10m" 
                }, 
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"      - Response received in {elapsed:.1f}s")
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                if result:
                    print(f"      ✓ Vision: {result[:60]}...")
                    return result
                else:
                    return "Visual clear but no detail"
            else:
                return "Visual analysis failed"
                
        except Exception as e:
            print(f"      ✗ Vision Error: {e}")
            return "Visual error"

    async def _get_strategic_response(self, visual_context, user_speech):
        """Step 2: Thinking Model Response"""
        if self.use_cloud_mind:
            return await self._get_cloud_strategic_response(visual_context, user_speech)
        
        print(f"   [4] Calling LOCAL MIND ({self.thinking_model})...")
        user_name = self.personal_memory.get('user_name', 'Dipesh')
        
        # Simplified prompt for faster response
        if user_speech:
            prompt = f"User says: {user_speech}\nGame scene: {visual_context}\nStrategy: Be a Hinglish friend. {user_name} is playing. Short reaction."
        else:
            prompt = f"Game scene: {visual_context}\nStrategy: 1 short Hinglish comment for {user_name}."

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_base_url}/api/generate", 
                json={
                    "model": self.thinking_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 25,
                        "num_ctx": 1024,
                        "num_thread": 8
                    },
                    "keep_alive": "10m"
                }, 
                timeout=60
            )
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                
                # Clean up
                result = result.strip('"').strip("'").strip()
                if "Reply:" in result:
                    result = result.split("Reply:")[-1].strip()
                
                if result:
                    print(f"      ✓ Response: {result[:60]}...")
                    return result, "success"
                else:
                    print("      ✗ Empty response from thinking model")
                    return None, None
            else:
                print(f"      ✗ Thinking API Error: {response.status_code}")
                print(f"         {response.text[:200]}")
                return None, None
                
        except requests.exceptions.Timeout:
            print("      ✗ TIMEOUT: Thinking model took too long!")
            return None, None
        except Exception as e:
            print(f"      ✗ Thinking Error: {e}")
            return None, None

    async def _get_cloud_strategic_response(self, visual_context, user_speech):
        """Step 2: Cloud Mind Response (Zero CPU Load + 70B Intelligence)"""
        print(f"   [4] Calling CLOUD MIND ({self.thinking_model})...")
        
        prompt = f"Scene: {visual_context}\nUser: {user_speech or '[Silent]'}\nRule: Short Hinglish strategic reaction."
        
        try:
            # Using standard requests for simple OpenAI-compatible API call
            headers = {"Authorization": f"Bearer {self.cloud_api_key}"}
            payload = {
                "model": self.thinking_model,
                "messages": [{"role": "system", "content": "You are Parthasarathi, a world-class life-long strategic partner. Speak Hinglish."},
                             {"role": "user", "content": prompt}],
                "max_tokens": 50
            }
            
            start_time = time.time()
            response = requests.post(f"{self.cloud_base_url}/chat/completions", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                reply = response.json()['choices'][0]['message']['content'].strip()
                print(f"      ✓ Cloud Response in {time.time()-start_time:.1f}s")
                return reply, "Cloud thought processed."
            return "Arre bhai, internet issue lag raha hai.", "Error"
        except Exception as e:
            return "Mind connection lost.", str(e)

    async def generate_response(self, user_speech=None, proactive=False):
        """Execute the Dual-Brain Pipeline with extensive logging"""
        try:
            print(f"\n{'='*60}")
            print(f"🎯 STARTING RESPONSE GENERATION")
            if user_speech:
                print(f"   Mode: User spoke '{user_speech}'")
            else:
                print(f"   Mode: Proactive observation")
            print(f"{'='*60}")
            
            # 1. Capture Image
            vision_data = await self.capture_vision_safe()
            combined_img = self.prepare_multimodal_input(vision_data)
            
            print("      - Processing image...")
            processed_img = self.image_processor.preprocess_for_vision_model(combined_img)
            img_b64 = self.image_processor.to_base64(processed_img)
            print(f"      ✓ Image ready ({len(img_b64)} bytes)")
            
            # 2. Get Visual Facts
            visual_facts = await self._get_visual_description(img_b64)
            
            # 3. Get Response
            reply, thought = await self._get_strategic_response(visual_facts, user_speech)
            
            if reply:
                print(f"\n✅ SUCCESS: Response generated!")
                print(f"{'='*60}\n")
                
                # Update stats
                self.personal_memory['interactions_count'] = self.personal_memory.get('interactions_count', 0) + 1
                self._save_memory()
                
                # Log
                full_context = f"Visual: {visual_facts} | Reply: {reply}"
                self._log_interaction(processed_img, user_speech or "[PROACTIVE]", full_context)
                
                return reply
            else:
                print(f"\n❌ FAILED: No response generated")
                print(f"{'='*60}\n")
                return None
                
        except Exception as e:
            print(f"\n❌ PIPELINE ERROR: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return None

    async def speak(self, text):
        """Convert text to speech and play"""
        if not text: 
            return
            
        print(f"\n💬 SPEAKING: \"{text}\"\n")
        
        try:
            temp_dir = self.base_dir / "src" / "core" / "tmp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"partha_{int(time.time() * 1000)}.mp3"
            
            print("   - Generating speech...")
            communicate = edge_tts.Communicate(text, self.tts_voice, rate="+20%")
            await communicate.save(str(temp_file))
            print("   ✓ Speech generated")
            
            # Play audio
            print("   - Playing audio...")
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.load(str(temp_file))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    print("   ✓ Audio played")
                except Exception as e:
                    print(f"   ✗ Pygame failed: {e}, using system player")
                    os.system(f"mpg123 -q '{temp_file}' 2>/dev/null &")
                    await asyncio.sleep(3)
            else:
                os.system(f"mpg123 -q '{temp_file}' 2>/dev/null &")
                await asyncio.sleep(3)
                
            # Cleanup
            await asyncio.sleep(0.5)
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ TTS Error: {e}")

    def _listen_callback(self, recognizer, audio):
        """Callback for background listener"""
        try:
            print("\n👂 Heard audio, recognizing...")
            speech_text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"🗣️  USER: {speech_text}")
            self.speech_queue.put(speech_text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"⚠️  Speech service error: {e}")
        except Exception as e:
            print(f"⚠️  STT Error: {e}")

    async def run(self):
        """Main loop with debug output"""
        print("\n" + "="*60)
        print("🚀 DEBUG MODE - INTERACTIVE GAMING PARTNER")
        print("="*60)
        if self.mic_available:
            print("🎙️  Microphone ready")
        else:
            print("⚠️  No microphone")
        print("🛑 Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        self.is_running = True
        stop_listening = None
        
        # Start voice listener
        if self.mic_available and self.mic:
            try:
                print("🎤 Calibrating microphone...")
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                stop_listening = self.recognizer.listen_in_background(
                    self.mic, 
                    self._listen_callback,
                    phrase_time_limit=10
                )
                print("✅ Voice recognition active\n")
            except Exception as e:
                print(f"❌ Mic error: {e}\n")
                stop_listening = lambda wait_for_stop=False: None
        else:
            stop_listening = lambda wait_for_stop=False: None

        try:
            # TEST: Generate one response immediately
            print("🧪 TESTING: Generating initial greeting...\n")
            greeting = await self.generate_response(proactive=True)
            if greeting:
                await self.speak(greeting)
            else:
                print("⚠️ Initial greeting failed - check logs above!\n")
            
            iteration = 0
            while self.is_running:
                iteration += 1
                
                # Debug: Show we're alive
                if iteration % 50 == 0:
                    print(f"💓 Heartbeat {iteration} - waiting for speech or proactive trigger...")
                
                # 1. Check for user speech
                try:
                    user_speech = self.speech_queue.get(timeout=0.5)
                    print(f"\n🎤 Got speech from queue: '{user_speech}'")
                    
                    response_text = await self.generate_response(user_speech=user_speech)
                    
                    if response_text:
                        await self.speak(response_text)
                    else:
                        print("⚠️ No response generated for user speech")
                    
                    self.last_observation_time = time.time()
                    
                except queue.Empty:
                    pass
                
                # 2. Proactive observation
                current_time = time.time()
                if current_time - self.last_observation_time > self.observation_interval:
                    print(f"\n⏰ Proactive trigger ({self.observation_interval}s elapsed)")
                    proactive_text = await self.generate_response(proactive=True)
                    
                    if proactive_text:
                        await self.speak(proactive_text)
                    
                    self.last_observation_time = current_time
                
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Shutdown requested")
        finally:
            self.is_running = False
            
            if stop_listening:
                stop_listening(wait_for_stop=False)
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            print("\n👋 Debug session ended")
            print(f"📊 Total interactions: {self.personal_memory.get('interactions_count', 0)}")

def main():
    """Entry point"""
    print("\n🔍 DIAGNOSTIC MODE - Running checks...\n")
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("⚠️  Ollama responded with unusual status")
    except:
        print("❌ Ollama is NOT running! Start it with: ollama serve")
        return
    
    print("\nStarting in 3 seconds...\n")
    time.sleep(3)
    
    partner = InteractiveGamingPartner()
    
    try:
        asyncio.run(partner.run())
    except KeyboardInterrupt:
        print("\n✅ Clean exit")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()