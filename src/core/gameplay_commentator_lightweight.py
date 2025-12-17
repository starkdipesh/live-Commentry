#!/usr/bin/env python3
"""
🎮 LIGHTWEIGHT AI Gameplay Commentary - Optimized for Low-Spec PCs
Works smoothly on older hardware with minimal resources

Requirements:
- 4GB RAM minimum
- CPU only (no GPU needed)
- Uses llava:latest (smaller, faster)
- Minimal image processing for speed
"""

import os
import asyncio
import base64
import io
import time
import random
from pathlib import Path
from datetime import datetime

# Image processing - lightweight
import mss
from PIL import Image, ImageEnhance

# Text-to-Speech - FREE
import edge_tts

# Audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# HTTP client for Ollama
import requests


class LightweightCommentator:
    """
    Lightweight gameplay commentator optimized for low-spec PCs
    - Minimal image processing
    - Faster model (llava:latest)
    - Lower resolution for speed
    - Reduced memory footprint
    """
    
    def __init__(self):
        """Initialize lightweight commentator"""
        # Ollama configuration - using existing model
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = "llava:latest"  # User already has this!
        
        # LIGHTWEIGHT Configuration
        self.screenshot_interval = 10  # Longer interval for slower PCs
        self.max_resolution = 512  # Much smaller for speed (was 1024-1280)
        self.jpeg_quality = 75  # Lower quality for speed (was 95)
        
        # Edge-TTS configuration
        self.tts_voice = "hi-IN-SwaraNeural"
        
        # Audio
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        
        # Memory - smaller for low RAM
        self.recent_comments = []
        self.max_memory = 5  # Reduced from 10
        
        # Stats
        self.comment_count = 0
        
        # Verify Ollama
        self._check_ollama()
        
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║   🎮 LIGHTWEIGHT GAMEPLAY COMMENTATOR 🎙️                     ║
║   Optimized for Low-Spec PCs - CPU Only                       ║
╚═══════════════════════════════════════════════════════════════╝

⚡ Lightweight Configuration:
   ✅ Model: {self.model_name} (you already have this!)
   ✅ Resolution: {self.max_resolution}px (fast processing)
   ✅ Quality: {self.jpeg_quality}% (speed optimized)
   ✅ Interval: {self.screenshot_interval}s (low CPU usage)
   ✅ Memory: Minimal footprint

💾 System Requirements:
   • RAM: 4GB minimum (8GB recommended)
   • CPU: Any dual-core processor
   • GPU: Not required!
   • Storage: ~5GB for model

🎙️ Ready to generate commentary on low-spec hardware!
        """)
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if self.model_name in models:
                    print(f"✅ Ollama running with {self.model_name}")
                else:
                    print(f"⚠️  Model {self.model_name} not found!")
                    print("   Available:", models)
        except:
            print("❌ Ollama not running. Start with: ollama serve")
    
    def _get_lightweight_prompt(self) -> str:
        """Optimized prompt for faster responses"""
        return """तुम एक gaming commentator हो। Screen देखो और SHORT Hindi commentary दो।

RULES:
1. VERY SHORT: Maximum 10-12 words only (तुरंत बोलो!)
2. SPECIFIC: Colors, numbers, actions बताओ
3. ENERGETIC: Natural और exciting बनो

Examples:
✅ "यो! लाल HP - danger zone!"
✅ "देखो 3 enemies - fight time!"
✅ "Perfect shot! Enemy down!"

IMPORTANT: Keep it VERY short and to the point!
"""
    
    def capture_screen_lightweight(self) -> Image.Image:
        """Fast screenshot capture with minimal processing"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # Quick resize for speed
            if img.width > self.max_resolution or img.height > self.max_resolution:
                if img.width > img.height:
                    new_width = self.max_resolution
                    new_height = int(img.height * (self.max_resolution / img.width))
                else:
                    new_height = self.max_resolution
                    new_width = int(img.width * (self.max_resolution / img.height))
                
                # Use BILINEAR for speed (faster than LANCZOS)
                img = img.resize((new_width, new_height), Image.Resampling.BILINEAR)
            
            # Minimal enhancement for speed
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)  # Very light sharpening
            
            return img
    
    def image_to_base64(self, img: Image.Image) -> str:
        """Convert to base64 with low quality for speed"""
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=self.jpeg_quality, optimize=False)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def generate_commentary(self, screenshot: Image.Image) -> str:
        """Generate commentary with speed optimizations"""
        try:
            start = time.time()
            
            # Convert image
            img_base64 = self.image_to_base64(screenshot)
            
            # Create prompt with recent comments
            prompt = self._get_lightweight_prompt()
            
            if self.recent_comments:
                prompt += f"\n\nRecent comments (don't repeat):\n"
                for c in self.recent_comments[-3:]:
                    prompt += f"- {c}\n"
            
            # Call Ollama with SPEED optimizations
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "images": [img_base64],
                    "stream": False,
                    "options": {
                        # SPEED-OPTIMIZED PARAMETERS
                        "temperature": 0.8,
                        "top_k": 30,           # Reduced for speed
                        "top_p": 0.85,         # Reduced for speed
                        "num_predict": 40,     # Short responses only!
                        "num_ctx": 2048,       # Smaller context for speed
                        "num_thread": 4,       # Use 4 CPU threads
                    }
                },
                timeout=20  # Shorter timeout
            )
            
            commentary = response.json()['response'].strip()
            
            # Update memory
            self.recent_comments.append(commentary)
            if len(self.recent_comments) > self.max_memory:
                self.recent_comments.pop(0)
            
            elapsed = time.time() - start
            print(f"   ⏱️  Generated in {elapsed:.1f}s")
            
            return commentary
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return self._get_fallback()
    
    def _get_fallback(self) -> str:
        """Quick fallback comments"""
        fallbacks = [
            "यो! Game चल रहा है!",
            "देखो क्या हो रहा है!",
            "अच्छा scene है!",
            "चलो देखते हैं!",
            "यार मस्त है!",
        ]
        return random.choice(fallbacks)
    
    async def speak_commentary(self, text: str):
        """Convert to speech - lightweight"""
        try:
            # Use temp file
            import tempfile
            temp_file = Path(tempfile.gettempdir()) / f"comm_{int(time.time()*1000)}.mp3"
            
            # Generate speech
            communicate = edge_tts.Communicate(text, self.tts_voice, rate="+20%")
            await communicate.save(str(temp_file))
            
            # Play
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
                
        except Exception as e:
            print(f"   ❌ TTS Error: {e}")
    
    async def run(self):
        """Main lightweight loop"""
        print(f"""
{'='*70}
🎮 STARTING LIGHTWEIGHT COMMENTARY
{'='*70}
⚡ Low CPU mode active
🎙️ Voice: {self.tts_voice}
⏱️  Interval: {self.screenshot_interval}s
🛑 Press Ctrl+C to stop
""")
        
        try:
            while True:
                self.comment_count += 1
                
                print(f"\n{'='*70}")
                print(f"🎬 Comment #{self.comment_count} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*70}")
                
                # Capture
                print("📸 Capturing (low res)...")
                screenshot = self.capture_screen_lightweight()
                print(f"   ✅ Captured {screenshot.width}x{screenshot.height}")
                
                # Generate
                print("🤖 Generating commentary...")
                commentary = self.generate_commentary(screenshot)
                print(f"\n💬 \"{commentary}\"\n")
                
                # Speak
                print("🎙️ Speaking...")
                await self.speak_commentary(commentary)
                print("   ✅ Done!\n")
                
                # Wait
                print(f"⏳ Waiting {self.screenshot_interval}s...")
                await asyncio.sleep(self.screenshot_interval)
                
        except KeyboardInterrupt:
            print(f"""
\n{'='*70}
🛑 STOPPED
{'='*70}
Total comments: {self.comment_count}
Thanks for using Lightweight Commentator! 🎮
            """)


async def main():
    """Entry point"""
    print("🚀 Starting Lightweight Commentator...")
    
    try:
        commentator = LightweightCommentator()
        await commentator.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Start Ollama: ollama serve")
        print("2. Check model: ollama list")
        print("3. If needed: ollama pull llava:latest")


if __name__ == "__main__":
    asyncio.run(main())
