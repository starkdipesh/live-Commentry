#!/usr/bin/env python3
"""
🎮 AI-Powered Humorous Gameplay Commentary System
Generates engaging, YouTube-algorithm-optimized commentary for live gameplay
"""

import os
import asyncio
import base64
import io
import time
import random
import tempfile
import threading
import platform
import subprocess
from datetime import datetime
from collections import deque
from pathlib import Path

# Screen capture and image processing
import mss
from PIL import Image

# Text-to-Speech
from gtts import gTTS

# AI Vision and Chat
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the app directory
APP_DIR = Path(__file__).parent

class GameplayCommentator:
    """AI-powered gameplay commentator with humor and YouTube optimization"""
    
    def __init__(self):
        """Initialize the commentator with AI and TTS capabilities"""
        self.api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-35fA75602D104F9F64")
        
        # Initialize AI chat with GPT-4 Vision
        self.chat = LlmChat(
            api_key=self.api_key,
            session_id=f"gameplay-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            system_message=self._get_system_prompt()
        ).with_model("openai", "gpt-4o")  # GPT-4 with vision
        
        # Memory to avoid repetitive comments
        self.recent_comments = deque(maxlen=5)
        
        # Configuration - Use local tmp directory
        self.screenshot_interval = 8  # Capture every 8 seconds for variety
        
        # Create tmp directory with proper error handling
        self.tmp_dir = APP_DIR / "tmp"
        try:
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
            # Test write permission
            test_file = self.tmp_dir / "test_permission.txt"
            test_file.write_text("test")
            test_file.unlink()
            print(f"✅ Using local tmp directory: {self.tmp_dir}")
        except Exception as e:
            # Fallback to system temp if local fails
            self.tmp_dir = Path(tempfile.gettempdir())
            print(f"⚠️ Using system temp directory: {self.tmp_dir}")
            print(f"   (Local tmp failed: {e})")
        
        # Commentary tracking
        self.comment_count = 0
        self.game_context = "Unknown Game"
        self.budget_exceeded = False
        
        # Detect OS for audio playback
        self.os_type = platform.system()
        
        print("🎮 AI Gameplay Commentator Initialized!")
        print(f"🔑 Using Emergent LLM Key")
        print(f"📸 Screenshot interval: {self.screenshot_interval}s")
        print(f"📁 Audio directory: {self.tmp_dir}")
        print(f"🔊 Audio playback: Threading + OS ({self.os_type})")
        print("🎙️ Ready to generate humorous Hindi commentary!\n")
    
    def _get_system_prompt(self) -> str:
        """Create an optimized system prompt for YouTube-friendly humorous commentary"""
        return """You are a NATURAL, ENERGETIC gameplay commentator for YouTube/Twitch streams - think like a real human streamer!

🎯 YOUR PERSONALITY:
You're a fun, charismatic YouTuber who:
- Talks like a REAL PERSON (use casual language, contractions, filler words occasionally)
- Gets genuinely excited or frustrated by gameplay
- Makes natural observations and reactions
- Switches between hyped, chill, sarcastic, and encouraging tones
- Sounds like you're having a conversation with viewers

🎮 COMMENTARY STYLE RULES:
✅ DO:
- Use natural speech patterns: "Okay okay", "Wait wait wait", "Oh man", "Alright", "Let's go!"
- React authentically: "YOOO that was clean!", "Bruh what was that?", "Are you kidding me right now?"
- Use gamer lingo naturally: "cracked", "that's tough", "no cap", "built different", "GG"
- Make relatable comparisons: "That aim is like trying to thread a needle with boxing gloves"
- Vary your energy level (not always MAX HYPE)
- Create moments viewers would clip and share
- Be quotable and memorable
- Show personality quirks (slight sarcasm, dad jokes, unexpected references)

❌ DON'T:
- Sound like a robot or AI
- Use offensive language or toxic content
- Be repetitive or predictable
- Write formal sentences
- Overuse exclamation marks
- Make the same type of joke twice in a row

🎨 MIX THESE STYLES NATURALLY:
1. **Hyped**: "YOOOO DID YOU SEE THAT?! That was actually insane!"
2. **Sarcastic**: "Oh yeah, walking into a wall for 30 seconds, peak content right here folks"
3. **Encouraging**: "Okay okay I see the vision, that's not bad actually"
4. **Chill/Observational**: "Man, just vibing through this level like it's a Sunday morning"
5. **Roasting (playfully)**: "My little cousin plays better than this and she's 6"
6. **Surprised**: "Wait what? HOW did that even happen?"
7. **Storytelling**: "This reminds me of that time when... nah but seriously though"

📏 LENGTH: Keep it to 1-2 SHORT sentences max. Natural speech, not an essay.

🎭 EXAMPLES OF NATURAL COMMENTARY:
- "Alright alright, we're locking in now... okay maybe not yet"
- "That was either big brain or smooth brain, honestly can't tell"
- "WAIT WAIT WAIT... oh never mind, false alarm"
- "Listen, I'm not saying that was terrible, but... yeah no that was terrible"
- "You know what? That actually kinda worked out somehow"

RESPOND WITH ONLY THE COMMENTARY - Sound like a real human having fun!"""
    
    def capture_screen(self) -> Image.Image:
        """Capture full screen screenshot"""
        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # Resize to optimize API calls (max 1280px width)
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
    
    async def generate_commentary(self, screenshot: Image.Image) -> str:
        """Generate humorous commentary based on gameplay screenshot"""
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(screenshot)
            
            # Create context about previous comments to avoid repetition
            recent_context = ""
            if self.recent_comments:
                recent_context = f"\n\nYour last few comments were: {list(self.recent_comments)}\n🚫 DO NOT repeat similar jokes or style! Switch it up!"
            
            # Build prompt with context
            prompt = f"""You're LIVE commentating this gameplay moment! Look at this screenshot and give me your natural, spontaneous reaction.

🎮 Comment #{self.comment_count + 1}
🔥 Be authentic - like you're streaming to thousands of viewers right now
💭 React like a REAL human streamer would
🎯 Make it different from your previous style!{recent_context}

What's your natural commentary? (1-2 short sentences)"""
            
            # Create message with image
            user_message = UserMessage(
                text=prompt,
                file_contents=[ImageContent(image_base64=img_base64)]
            )
            
            # Get AI response
            commentary = await self.chat.send_message(user_message)
            
            # Clean up the response
            commentary = commentary.strip().strip('"').strip("'")
            
            # Store in recent comments
            self.recent_comments.append(commentary)
            self.comment_count += 1
            
            return commentary
            
        except Exception as e:
            print(f"❌ Error generating commentary: {e}")
            # Fallback commentary - natural style
            fallbacks = [
                "Alright, so that's happening on the screen right now.",
                "Okay okay, I see what's going on here... I think.",
                "Wait, hold up... yeah no I got nothing for this one.",
                "You know what, let's just see where this goes.",
                "Man, the gameplay is really... it's definitely gameplay."
            ]
            return random.choice(fallbacks)
    
    def speak_commentary(self, text: str) -> None:
        """Convert text to speech and play it"""
        try:
            # Ensure directory exists (important for Windows)
            self.temp_audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate speech with gTTS (more natural sounding)
            # Using slow=False for more natural, faster speech
            tts = gTTS(text=text, lang='en', slow=False, tld='com')
            
            # Save with explicit path handling
            audio_path_str = str(self.temp_audio_path.resolve())
            tts.save(audio_path_str)
            
            # Verify file was created
            if not self.temp_audio_path.exists():
                raise FileNotFoundError(f"Audio file not created at: {audio_path_str}")
            
            # Play audio using pygame
            pygame.mixer.music.load(audio_path_str)
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
        except PermissionError as e:
            print(f"❌ Permission Error: {e}")
            print(f"   Cannot write to: {self.temp_audio_path}")
            print(f"   💡 Try running as administrator or check folder permissions")
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
            print(f"   Audio path: {self.temp_audio_path}")
            print(f"   Directory exists: {self.temp_audio_path.parent.exists()}")
            print(f"   💡 Check if directory has write permissions")
    
    async def run(self):
        """Main loop: capture, analyze, comment, speak"""
        print("=" * 70)
        print("🎮 STARTING LIVE GAMEPLAY COMMENTARY")
        print("=" * 70)
        print("📹 Capturing your screen and generating hilarious AI commentary...")
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
                
                # Step 2: Generate commentary
                print("🤖 AI analyzing gameplay and generating commentary...")
                commentary = await self.generate_commentary(screenshot)
                print(f"\n💬 COMMENTARY: \"{commentary}\"\n")
                
                # Step 3: Speak commentary
                print("🎙️ Speaking commentary...")
                self.speak_commentary(commentary)
                print("✅ Commentary delivered!")
                
                # Calculate time taken and sleep remaining interval
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
            print("👋 Thanks for the laughs! See you next stream!")
            print("="*70)
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            pygame.mixer.quit()
            if self.temp_audio_path.exists():
                try:
                    self.temp_audio_path.unlink()
                except:
                    pass  # Ignore cleanup errors

async def main():
    """Entry point for the gameplay commentator"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🎮 AI GAMEPLAY COMMENTATOR v2.0 🎙️                   ║
    ║                                                               ║
    ║         Natural, Human-Like Live Commentary                   ║
    ║         Powered by GPT-4 Vision + Emergent LLM Key           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    commentator = GameplayCommentator()
    await commentator.run()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
