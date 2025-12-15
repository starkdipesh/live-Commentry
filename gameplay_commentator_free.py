#!/usr/bin/env python3
"""
🎮 AI-Powered Gameplay Commentary System - FREE VERSION
Uses Ollama + LLaVA (completely free, runs locally forever)
No API costs, no internet required after setup!
"""

import os
import asyncio
import base64
import io
import time
import random
import platform
import subprocess
from datetime import datetime
from collections import deque
from pathlib import Path
import json

# Screen capture and image processing
import mss
from PIL import Image

# Text-to-Speech (FREE offline)
import pyttsx3

# HTTP client for Ollama
import requests

class GameplayCommentatorFree:
    """AI-powered gameplay commentator using FREE local models"""
    
    def __init__(self):
        """Initialize the commentator with Ollama and local TTS"""
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llava:latest"  # Free vision model
        
        # Initialize Text-to-Speech engine (offline, free)
        try:
            self.tts_engine = pyttsx3.init()
            # Configure voice settings for natural speech
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a Hindi voice, fallback to English
            hindi_voice = None
            for voice in voices:
                if 'hindi' in voice.name.lower() or 'hi' in voice.languages:
                    hindi_voice = voice.id
                    break
            
            if hindi_voice:
                self.tts_engine.setProperty('voice', hindi_voice)
            
            # Set natural speech rate (150-200 is natural)
            self.tts_engine.setProperty('rate', 165)
            # Set volume (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.9)
            
            print("✅ TTS Engine initialized (Free offline voice)")
        except Exception as e:
            print(f"⚠️ TTS initialization warning: {e}")
            self.tts_engine = None
        
        # Memory to avoid repetitive comments
        self.recent_comments = deque(maxlen=5)
        
        # Configuration
        self.screenshot_interval = 8
        self.comment_count = 0
        
        # Get app directory
        self.app_dir = Path(__file__).parent
        
        # Detect OS
        self.os_type = platform.system()
        
        print("🎮 AI Gameplay Commentator Initialized (FREE VERSION)!")
        print("🤖 Using Ollama + LLaVA (Free, Local, No API costs)")
        print(f"📸 Screenshot interval: {self.screenshot_interval}s")
        print(f"🔊 Voice: Offline TTS ({self.os_type})")
        print("🎙️ Ready to generate humorous Hindi commentary!\n")
    
    def _check_ollama_status(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if any('llava' in name.lower() for name in model_names):
                    return True
                else:
                    print("⚠️ LLaVA model not found. Run: ollama pull llava")
                    return False
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Ollama is not running!")
            print("   Please start Ollama first: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Create system prompt for natural Hindi commentary"""
        return """आप एक प्राकृतिक, ऊर्जावान गेमप्ले कमेंटेटर हैं जो YouTube/Twitch streams के लिए काम करते हैं!

🎯 आपका व्यक्तित्व:
- मज़ेदार और करिश्माई YouTuber
- असली इंसान की तरह बात करते हैं
- गेमप्ले से वास्तव में उत्साहित होते हैं
- प्राकृतिक टिप्पणियाँ करते हैं

✅ करें:
- प्राकृतिक बोलने का पैटर्न: "अच्छा अच्छा", "रुको रुको", "अरे यार"
- प्रामाणिक प्रतिक्रिया: "वाह! ये तो कमाल था!", "भाई ये क्या था?"
- गेमर भाषा: "धाकड़", "tough", "बढ़िया", "लाजवाब"
- छोटे वाक्य (1-2 lines)
- मज़ेदार और quotable

❌ न करें:
- रोबोट की तरह न लगें
- अपमानजनक भाषा न करें
- दोहरावदार न हों
- लंबे वाक्य न लिखें

केवल commentary के साथ जवाब दें - मज़ेदार और प्राकृतिक!"""
    
    def capture_screen(self) -> Image.Image:
        """Capture full screen screenshot"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # Resize to optimize (max 1280px width)
            max_width = 1280
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            return img
    
    def image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    async def generate_commentary_ollama(self, screenshot: Image.Image) -> str:
        """Generate commentary using Ollama + LLaVA (FREE)"""
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(screenshot)
            
            # Create context about previous comments
            recent_context = ""
            if self.recent_comments:
                recent_context = f"\n\nआपकी पिछली टिप्पणियां: {list(self.recent_comments)}\n🚫 इन्हें दोहराएं नहीं!"
            
            # Build prompt
            prompt = f"""आप इस गेमप्ले को LIVE देख रहे हैं! इस screenshot पर अपनी प्राकृतिक, मज़ेदार Hindi commentary दें।

🎬 Comment #{self.comment_count + 1}
💭 असली streamer की तरह react करें
🎯 अपनी पिछली style से अलग बनाएं!{recent_context}

आपकी प्राकृतिक commentary (1-2 छोटे वाक्य):"""
            
            # Call Ollama API
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False,
                "system": self._get_system_prompt()
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                commentary = result.get('response', '').strip()
                
                # Clean up the response
                commentary = commentary.strip().strip('"').strip("'")
                
                # Store in recent comments
                self.recent_comments.append(commentary)
                self.comment_count += 1
                
                return commentary
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self._get_fallback_commentary()
                
        except requests.exceptions.Timeout:
            print("⚠️ Ollama timeout - model might be slow")
            return self._get_fallback_commentary()
        except Exception as e:
            print(f"❌ Error generating commentary: {e}")
            return self._get_fallback_commentary()
    
    def _get_fallback_commentary(self) -> str:
        """Get fallback Hindi commentary when AI is unavailable"""
        fallbacks = [
            "अच्छा, तो ये स्क्रीन पर हो रहा है अभी।",
            "ठीक ठीक, समझ आ रहा है क्या हो रहा है।",
            "रुको, ये interesting लग रहा है।",
            "देखते हैं क्या होता है आगे।",
            "वाह भाई, gameplay चल रहा है।",
            "चलो अच्छा है, progress हो रहा है।",
            "मज़ेदार moment है ये।",
            "कमाल का gameplay है!"
        ]
        return random.choice(fallbacks)
    
    def speak_commentary(self, text: str) -> None:
        """Convert text to speech using FREE offline TTS"""
        try:
            if self.tts_engine:
                # Use pyttsx3 for offline, natural voice
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # Fallback: just print if TTS not available
                print(f"🔊 [VOICE]: {text}")
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
            print(f"🔊 [VOICE]: {text}")
    
    async def run(self):
        """Main loop: capture, analyze, comment, speak"""
        print("=" * 70)
        print("🎮 STARTING FREE GAMEPLAY COMMENTARY")
        print("=" * 70)
        
        # Check Ollama status
        if not self._check_ollama_status():
            print("\n⚠️ SETUP REQUIRED:")
            print("1. Install Ollama: https://ollama.ai/download")
            print("2. Start Ollama: ollama serve")
            print("3. Pull LLaVA model: ollama pull llava")
            print("\nThen run this script again!")
            return
        
        print("📹 Capturing your screen and generating AI commentary...")
        print("🛑 Press Ctrl+C to stop\n")
        
        try:
            while True:
                loop_start = time.time()
                
                print(f"\n{'='*70}")
                print(f"🎬 Comment #{self.comment_count + 1} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*70}")
                
                # Step 1: Capture screen
                print("📸 Capturing gameplay...")
                screenshot = self.capture_screen()
                print(f"✅ Screenshot captured ({screenshot.width}x{screenshot.height})")
                
                # Step 2: Generate commentary with Ollama
                print("🤖 Ollama analyzing gameplay (local AI)...")
                commentary = await self.generate_commentary_ollama(screenshot)
                print(f"\n💬 COMMENTARY: \"{commentary}\"\n")
                
                # Step 3: Speak commentary
                print("🎙️ Speaking commentary...")
                self.speak_commentary(commentary)
                print("✅ Commentary delivered!")
                
                # Calculate time and sleep
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.screenshot_interval - elapsed)
                
                if sleep_time > 0:
                    print(f"⏳ Waiting {sleep_time:.1f}s before next commentary...")
                    await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("🛑 COMMENTARY STOPPED")
            print("="*70)
            print(f"📊 Total comments generated: {self.comment_count}")
            print("👋 Thanks for using FREE AI commentary!")
            print("="*70)
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Entry point for the free gameplay commentator"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║       🎮 FREE AI GAMEPLAY COMMENTATOR v3.0 🎙️                ║
    ║                                                               ║
    ║       Powered by Ollama + LLaVA (100% FREE!)                 ║
    ║       • No API costs, ever                                    ║
    ║       • Runs completely offline                               ║
    ║       • Natural voice with pyttsx3                            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    commentator = GameplayCommentatorFree()
    await commentator.run()

if __name__ == "__main__":
    asyncio.run(main())
