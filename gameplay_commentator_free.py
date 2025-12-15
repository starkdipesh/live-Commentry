#!/usr/bin/env python3
"""
🎮 AI-Powered Gameplay Commentary System - FREE VERSION
Uses Ollama + LLaVA (completely free, runs locally forever)
No API costs, no internet required after setup!
With NATURAL HUMANOID VOICE using Edge-TTS!
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

# Text-to-Speech (FREE with natural voice)
import edge_tts

# Audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# HTTP client for Ollama
import requests

class GameplayCommentatorFree:
    """AI-powered gameplay commentator using FREE local models"""
    
    def __init__(self):
        """Initialize the commentator with Ollama and natural TTS"""
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llava:latest"  # Free vision model
        
        # Edge-TTS Voice Configuration (FREE, Natural, Human-like)
        # Hindi voices available in Edge-TTS
        self.voice_options = [
            "hi-IN-SwaraNeural",      # Female, very natural
            "hi-IN-MadhurNeural",     # Male, clear and natural
        ]
        self.current_voice = self.voice_options[0]  # Default to female voice
        
        # Initialize pygame for audio playback
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ Pygame audio initialized")
            except Exception as e:
                print(f"⚠️ Pygame initialization warning: {e}")
        
        # Memory to avoid repetitive comments (increased for better diversity)
        self.recent_comments = deque(maxlen=10)
        
        # Configuration
        self.screenshot_interval = 6  # Reduced for more dynamic commentary
        self.comment_count = 0
        
        # Last screenshot for comparison (to detect scene changes)
        self.last_screenshot_hash = None
        
        # Get app directory and create tmp folder
        self.app_dir = Path(__file__).parent
        self.tmp_dir = self.app_dir / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect OS
        self.os_type = platform.system()
        
        print("🎮 AI Gameplay Commentator Initialized (FREE VERSION)!")
        print("🤖 Using Ollama + LLaVA (Free, Local, No API costs)")
        print(f"📸 Screenshot interval: {self.screenshot_interval}s")
        print(f"🎙️ Voice: Edge-TTS ({self.current_voice})")
        print("✨ Natural humanoid voice with emotion!")
        print("🎯 Ready to generate humorous Hindi commentary!\n")
    
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
        return """आप एक मज़ेदार, ऊर्जावान गेमप्ले कमेंटेटर हैं जो YouTube/Twitch streams के लिए काम करते हैं!

🎯 आपका व्यक्तित्व:
- HYPER मज़ेदार और करिश्माई YouTuber/Streamer
- असली इंसान की तरह spontaneous reactions
- गेमप्ले से genuinely उत्साहित और surprised
- प्राकृतिक, अनपेक्षित टिप्पणियाँ
- हर बार UNIQUE और FRESH content

✅ करें (विविधता बनाए रखें):
- प्राकृतिक fillers: "अरे वाह", "ओहो", "देखो देखो", "यार", "भाई", "अबे", "अजी"
- EPIC प्रतिक्रियाएं: "वाह क्या scene है!", "यो यो यो!", "होली मोली!", "पगलाए हो क्या!"
- गेमर स्लैंग (मिक्स): "OP", "pro moves", "noob moment", "clutch", "GG", "धांसू", "छक्का", "धमाका"
- हास्य: "भाई किसने सिखाया ये?", "मेरी तो सांसें रुक गईं!", "पड़ोसी जग जाएंगे!"
- छोटे, punchy वाक्य (1 line, max 10 words)
- VARIED शब्द हर बार - NEVER repeat patterns!
- Screen details पर focus: colors, actions, UI elements

❌ STRICTLY न करें:
- पिछली comments repeat न करें
- Same structure या pattern दोबारा न दें
- Generic boring comments नहीं
- Robot जैसा formal tone नहीं
- लंबे paragraphs नहीं

🎬 CRITICAL: स्क्रीन पर SPECIFIC चीज़ें देखें और उन पर react करें (colors, characters, text, actions)!
केवल commentary दें - छोटा, मज़ेदार, और हर बार TOTALLY DIFFERENT!"""
    
    def capture_screen(self) -> Image.Image:
        """Capture full screen screenshot with optimized quality"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # Resize to optimize (increased to 1024px for better accuracy)
            # Smaller than before for speed, but with better quality preservation
            max_width = 1024
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                # Use LANCZOS for high-quality downscaling
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Enhance image slightly for better AI analysis
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)  # Slight sharpening
            
            return img
    
    def image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string with high quality"""
        buffered = io.BytesIO()
        # Increased quality to 95 for better detail preservation
        img.save(buffered, format="JPEG", quality=95, optimize=True)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    async def generate_commentary_ollama(self, screenshot: Image.Image) -> str:
        """Generate commentary using Ollama + LLaVA (FREE) - Optimized for speed and variety"""
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(screenshot)
            
            # Create context about previous comments with emphasis
            recent_context = ""
            if self.recent_comments:
                recent_list = list(self.recent_comments)[-5:]  # Last 5 only
                recent_context = f"\n\n⚠️ आपकी पिछली 5 टिप्पणियां:\n{chr(10).join([f'- {c}' for c in recent_list])}\n\n🚫 FORBIDDEN: इन शब्दों/phrases को दोबारा use न करें!\n✅ REQUIRED: पूरी तरह DIFFERENT style और words use करें!"
            
            # Add variety hints based on comment count
            variety_hints = [
                "Screen पर SPECIFIC details देखें और उन पर बोलें!",
                "इस बार TOTALLY अलग angle से comment करें!",
                "UNEXPECTED reaction दें - surprise करें!",
                "Screen के colors/text/characters पर FOCUS करें!",
                "HUMOROUS observation करें जो किसी ने न सोचा हो!"
            ]
            current_hint = variety_hints[self.comment_count % len(variety_hints)]
            
            # Build enhanced prompt with better instructions
            prompt = f"""🎮 LIVE गेमप्ले का screenshot देखें और इस पर एक मज़ेदार, unique commentary दें!

📸 Comment #{self.comment_count + 1}
🎯 {current_hint}
💡 Screen में क्या SPECIFIC चीज़ें दिख रही हैं? उन पर बोलें!
🎭 Fresh reaction - हर बार नया अंदाज़!{recent_context}

📝 आपकी मज़ेदार commentary (केवल 1 छोटा वाक्य, max 12 words):"""
            
            # Call Ollama API with optimized parameters
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False,
                "system": self._get_system_prompt(),
                "options": {
                    "temperature": 0.9,      # Higher for more creativity/variety
                    "top_p": 0.95,           # Higher for diverse vocabulary
                    "top_k": 50,             # More word choices
                    "num_predict": 50,       # Limit tokens for shorter responses
                    "repeat_penalty": 1.5    # Strongly penalize repetition
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=20  # Reduced from 30s to 20s for faster timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                commentary = result.get('response', '').strip()
                
                # Clean up the response aggressively
                commentary = commentary.strip().strip('"').strip("'").strip('`')
                # Remove any markdown or extra formatting
                commentary = commentary.replace('**', '').replace('*', '')
                # Take only first sentence if multiple
                if '।' in commentary:
                    commentary = commentary.split('।')[0] + '।'
                elif '!' in commentary:
                    commentary = commentary.split('!')[0] + '!'
                
                # Ensure it's not too long
                words = commentary.split()
                if len(words) > 15:
                    commentary = ' '.join(words[:15])
                
                # Check if it's too similar to recent ones
                if self._is_too_similar(commentary):
                    print("⚠️ Commentary too similar to recent ones, using fallback")
                    return self._get_fallback_commentary()
                
                # Store in recent comments
                self.recent_comments.append(commentary)
                self.comment_count += 1
                
                return commentary
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self._get_fallback_commentary()
                
        except requests.exceptions.Timeout:
            print("⚠️ Ollama timeout (>20s) - using fallback")
            return self._get_fallback_commentary()
        except Exception as e:
            print(f"❌ Error generating commentary: {e}")
            return self._get_fallback_commentary()
    
    def _is_too_similar(self, new_comment: str) -> bool:
        """Check if new comment is too similar to recent ones"""
        if not self.recent_comments:
            return False
        
        new_words = set(new_comment.lower().split())
        for old_comment in list(self.recent_comments)[-3:]:  # Check last 3
            old_words = set(old_comment.lower().split())
            # Calculate word overlap
            if len(new_words & old_words) > len(new_words) * 0.6:  # >60% overlap
                return True
        return False
    
    def _get_fallback_commentary(self) -> str:
        """Get fallback Hindi commentary when AI is unavailable - Enhanced with more variety"""
        fallbacks = [
            "अरे वाह! ये तो देखना बनता है!",
            "यार, scene तो धांसू है!",
            "ओहो! क्या चल रहा है ये?",
            "भाई भाई, ये तो मस्त है!",
            "देखो देखो, कुछ होने वाला है!",
            "यो! Game तो fire हो रहा है!",
            "अजी, इससे अच्छा और क्या?",
            "पगला गया है क्या! कमाल है!",
            "होली मोली! क्या scene है!",
            "वाह क्या बात है भाई!",
            "अबे ये तो unexpected था!",
            "GG! धमाका हो गया!",
            "प्रो मूव्स चल रहे हैं!",
            "यार क्या gameplay है!",
            "छक्का मारा इसने!",
            "भाई साहब, लाजवाब है!",
            "अरे बाप रे! OP moment!",
            "क्या सीन है यार!",
            "धांसू content मिल रहा है!",
            "मज़ा आ गया बोस!"
        ]
        # Use recent comments to avoid picking same fallback
        used_recently = list(self.recent_comments)[-3:]
        available = [f for f in fallbacks if f not in used_recently]
        if available:
            return random.choice(available)
        return random.choice(fallbacks)
    
    async def speak_commentary(self, text: str) -> None:
        """Convert text to speech using FREE Edge-TTS with natural voice"""
        try:
            # Create unique audio file path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            audio_file = self.tmp_dir / f"commentary_{timestamp}.mp3"
            
            # Generate speech with Edge-TTS (very natural, human-like)
            communicate = edge_tts.Communicate(text, self.current_voice)
            await communicate.save(str(audio_file))
            
            # Verify file was created
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not created: {audio_file}")
            
            print(f"✅ Audio generated: {audio_file.name}")
            
            # Play audio
            await self._play_audio(audio_file)
            
            # Cleanup after playback
            try:
                if audio_file.exists():
                    audio_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors
                
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
            print(f"🔊 [VOICE]: {text}")
    
    async def _play_audio(self, audio_file: Path) -> None:
        """Play audio file using pygame or system player"""
        try:
            if PYGAME_AVAILABLE:
                # Use pygame for reliable playback
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                    
            else:
                # Fallback to system audio player
                if self.os_type == "Windows":
                    os.system(f'start /min "" "{audio_file}"')
                elif self.os_type == "Darwin":  # macOS
                    os.system(f'afplay "{audio_file}"')
                else:  # Linux
                    # Try common Linux players
                    for player in ['mpg123', 'ffplay', 'cvlc']:
                        if subprocess.run(['which', player], capture_output=True).returncode == 0:
                            subprocess.run([player, '-q', str(audio_file)], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                            break
                
                # Wait estimated time for playback
                await asyncio.sleep(3)
                
        except Exception as e:
            print(f"⚠️ Audio playback warning: {e}")
    
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
                await self.speak_commentary(commentary)
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
