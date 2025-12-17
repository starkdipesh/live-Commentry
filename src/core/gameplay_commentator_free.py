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
from PIL import Image, ImageEnhance

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
        """Create system prompt for LIVE, natural, unrehearsed commentary"""
        return """आप एक LIVE streamer हैं जो अभी-अभी real-time में gameplay देख रहे हैं! असली ज़िंदगी की तरह react करें!

🎯 LIVE STREAMER व्यक्तित्व:
- जैसे दोस्त से बात कर रहे हों - बिल्कुल casual
- अधूरे वाक्य OK हैं - "अरे ये... वाह यार!"
- सोचते हुए बोलें - "तो... अब क्या... ओह!"
- Real emotions - excited, surprised, confused, happy
- Stream of consciousness - जो दिमाग में आए वो बोलें

✅ LIVE FEEL के लिए करें:
- अधूरे वाक्य: "अरे रुको... ये तो...", "देखो देखो... वाह!"
- Thinking out loud: "अब क्या होगा यार...", "हम्म... interesting..."
- Live reactions: "अभी... अभी... हां! हो गया!", "रुको रुको... oh no!"
- Natural fillers: "तो", "यार", "देखो", "अच्छा", "हम्म", "उफ्फ"
- Incomplete thoughts: "ये... wow!", "भाई... seriously?"
- Talk to viewers: "guys देखो!", "यार trust me", "बताओ यार"
- Real emotions: "डर लग रहा है", "excited हूं", "tension हो रही"
- Gaming feel: "लगे रहो", "careful careful", "go go go!", "नहीं नहीं!"

✅ स्क्रीन पर जो EXACTLY दिख रहा उस पर react करें:
- Colors: "लाल light flash हुआ!", "सब dark हो गया"
- Movement: "jump किया!", "दौड़ रहा है fast", "गिर गया अभी"
- Text/UI: "health low है!", "score बढ़ा", "message आया"
- Changes: "scene बदल गया!", "नया area है", "enemy आया"

❌ AVOID करें:
- Scripted या rehearsed sound न करें
- Perfect sentences - too formal लगता है
- पिछली बार जो बोले वो फिर न बोलें
- Generic description - specific चीज़ों पर baat करें
- Same pattern bar bar नहीं

🎬 याद रखें: आप LIVE हैं! जैसे खुद game खेल रहे हों और दोस्तों को बता रहे हों!
केवल 1 छोटा reaction दें - natural, spontaneous, real!"""
    
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
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)  # Slight sharpening for better detail
            
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
            
            # Add LIVE streaming hints that change dynamically
            live_hints = [
                "पहली नज़र में जो दिखे उस पर turant react करें - unfiltered!",
                "सोचते हुए बोलें जैसे live में होता है - thinking out loud!",
                "Screen पर कुछ बदला? उस change पर immediately react करें!",
                "जो feel हो रहा वो express करें - excited, confused, scared!",
                "Dost से बात की तरह - casual, natural, incomplete sentences OK!",
                "Stream of consciousness - जो mind में आए वो बोलें!",
                "Live moment capture करें - अधूरा वाक्य भी chalega!",
                "Viewers को बताओ जैसे खुद खेल रहे हो!"
            ]
            current_hint = live_hints[self.comment_count % len(live_hints)]
            
            # Build LIVE streaming style prompt
            prompt = f"""🔴 LIVE STREAMING! आप अभी real-time में ये gameplay देख रहे हैं!

🎮 Moment #{self.comment_count + 1}
💭 {current_hint}
👀 स्क्रीन पर EXACTLY क्या हो रहा है? जैसे live reaction हो!
🎙️ Unscripted, spontaneous - जो दिमाग में आया वो बोलो!{recent_context}

📢 आपका LIVE reaction (natural, can be incomplete, max 10 words):"""
            
            # Call Ollama API with parameters optimized for LIVE feel
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False,
                "system": self._get_system_prompt(),
                "options": {
                    "temperature": 1.0,      # Maximum creativity for spontaneous feel
                    "top_p": 0.95,           # Diverse vocabulary
                    "top_k": 60,             # Even more word choices for variety
                    "num_predict": 40,       # Shorter for quick, punchy reactions
                    "repeat_penalty": 1.8,   # Very strong anti-repetition for live feel
                    "presence_penalty": 0.6  # Encourage new topics/angles
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
                
                # Clean up gently - preserve natural, live feel
                commentary = commentary.strip().strip('"').strip("'").strip('`')
                # Remove markdown but keep natural punctuation
                commentary = commentary.replace('**', '').replace('*', '')
                
                # Keep it short and punchy (live streaming style)
                # Don't force complete sentences - incomplete is OK for live feel
                words = commentary.split()
                if len(words) > 12:
                    # Take first 10-12 words for quick, live reactions
                    commentary = ' '.join(words[:12])
                    # Add natural ending if needed
                    if not commentary.endswith(('!', '?', '।', '...')):
                        commentary += '!'
                
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
        """Get fallback Hindi commentary with LIVE streaming feel"""
        # LIVE streaming style fallbacks - natural, spontaneous
        fallbacks = [
            "अरे... ये देखो यार!",
            "रुको रुको... वाह!",
            "ओह! ये तो... nice!",
            "हम्म... interesting scene है!",
            "देखो guys... ये क्या है!",
            "अभी... अभी कुछ होगा!",
            "यो! check करो ये!",
            "भाई... seriously?",
            "अच्छा तो... ओह wow!",
            "एक sec... damn!",
            "यार trust me... epic है!",
            "so... let's see... nice!",
            "अरे नहीं... wait... हां!",
            "ओहो... unexpected था!",
            "guys... देखो ये!",
            "तो अब... hmm... cool!",
            "अबे... क्या scene!",
            "रुको... ये तो... pro!",
            "oh man... intense है!",
            "चलो देखते... wow!",
            "एक min... amazing!",
            "यार... no way!",
            "देखो... होने वाला कुछ!",
            "so excited guys!",
            "अरे... tension हो रही!",
            "हम्म... scary लग रहा!",
            "go go go... yes!",
            "careful... ओह!",
            "nice nice... good!",
            "यार... feeling good!"
        ]
        # Use recent comments to avoid picking same fallback
        used_recently = list(self.recent_comments)[-3:]
        available = [f for f in fallbacks if f not in used_recently]
        if available:
            return random.choice(available)
        return random.choice(fallbacks)
    
    async def speak_commentary(self, text: str) -> None:
        """Convert text to speech using FREE Edge-TTS with natural voice - Optimized for speed"""
        try:
            # Create unique audio file path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            audio_file = self.tmp_dir / f"commentary_{timestamp}.mp3"
            
            # Generate speech with Edge-TTS (very natural, human-like)
            # Added rate adjustment for faster speech
            communicate = edge_tts.Communicate(
                text, 
                self.current_voice,
                rate="+15%"  # Slightly faster for more energetic commentary
            )
            await communicate.save(str(audio_file))
            
            # Verify file was created
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not created: {audio_file}")
            
            print(f"✅ Audio generated: {audio_file.name}")
            
            # Play audio (non-blocking for faster loop)
            await self._play_audio(audio_file)
            
            # Cleanup after playback (async to not block)
            asyncio.create_task(self._cleanup_audio(audio_file))
                
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
            print(f"🔊 [VOICE]: {text}")
    
    async def _cleanup_audio(self, audio_file: Path) -> None:
        """Async cleanup of audio file"""
        try:
            await asyncio.sleep(1)  # Wait a bit before cleanup
            if audio_file.exists():
                audio_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors
    
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
