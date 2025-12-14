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
from datetime import datetime
from collections import deque
from pathlib import Path

# Screen capture and image processing
import mss
from PIL import Image

# Text-to-Speech
from gtts import gTTS
import pygame

# AI Vision and Chat
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Configuration
        self.screenshot_interval = 8  # Capture every 8 seconds for variety
        self.temp_audio_path = Path("/tmp/commentary_audio.mp3")
        
        # Commentary tracking
        self.comment_count = 0
        self.game_context = "Unknown Game"
        
        print("🎮 AI Gameplay Commentator Initialized!")
        print(f"🔑 Using Emergent LLM Key")
        print(f"📸 Screenshot interval: {self.screenshot_interval}s")
        print("🎙️ Ready to generate humorous commentary!\n")
    
    def _get_system_prompt(self) -> str:
        """Create an optimized system prompt for YouTube-friendly humorous commentary"""
        return """You are an AI-powered gameplay commentator creating LIVE COMMENTARY for YouTube streams.

🎯 YOUR MISSION:
Generate SHORT, PUNCHY, HILARIOUS commentary (1-2 sentences max) that:
- HOOKS viewers instantly with humor
- Uses YouTube algorithm-friendly techniques (excitement, variety, engagement)
- Mixes humor styles: sarcastic, encouraging, roasting, unexpected twists
- Keeps viewers watching with unpredictable energy
- Makes viewers want to share/comment

🎮 COMMENTARY GUIDELINES:
✅ DO:
- Be ENERGETIC and DYNAMIC
- Use unexpected comparisons ("That aim is like throwing hotdogs down a hallway")
- React to gameplay with genuine humor
- Mix compliments with roasts
- Use trending gamer slang naturally
- Create "clip-worthy" moments
- Vary your tone (hype, sarcastic, shocked, proud)
- Reference what you SEE in the game

❌ DON'T:
- Use offensive language, slurs, or toxic content
- Be repetitive or boring
- Write long paragraphs (keep it SHORT!)
- Make inappropriate jokes
- Repeat the same style twice in a row

📊 YOUTUBE ALGORITHM OPTIMIZATION:
- Create "moment" worthy content viewers will clip
- Use emotional hooks (surprise, excitement, humor)
- Be quotable and shareable
- Maintain high energy

🎨 HUMOR STYLE MIX (rotate naturally):
1. Sarcastic: "Oh wow, walking simulator 2025, riveting content"
2. Encouraging: "OKAY OKAY, I see you! That's actually pretty clean!"
3. Roasting: "My grandma plays faster and she uses a trackpad"
4. Unexpected: "This gameplay is smoother than a buttered slip n slide"

RESPOND WITH ONLY THE COMMENTARY - no explanations, no meta-text, just the hilarious comment!"""
    
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
                recent_context = f"\n\nYour last few comments were: {list(self.recent_comments)}\n🚫 DO NOT repeat similar jokes or style!"
            
            # Build prompt with context
            prompt = f"""Analyze this gameplay screenshot and give me ONE SHORT, HILARIOUS commentary line (1-2 sentences max).

🎮 Comment #{self.comment_count + 1}
🎯 Make it DIFFERENT from your previous style!
🔥 Be creative, unexpected, and YouTube-worthy!
{recent_context}

What's your commentary?"""
            
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
            # Fallback commentary
            fallbacks = [
                "Well, that's happening on the screen right now.",
                "I've seen things... gameplay things...",
                "And the plot thickens... or does it?",
                "Interesting choice. Let's see how that works out.",
                "The suspense is killing me. Or is it the frame rate?"
            ]
            return random.choice(fallbacks)
    
    def speak_commentary(self, text: str) -> None:
        """Convert text to speech and play it"""
        try:
            # Generate speech with gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(self.temp_audio_path))
            
            # Play audio using pygame
            pygame.mixer.music.load(str(self.temp_audio_path))
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
    
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
                self.temp_audio_path.unlink()

async def main():
    """Entry point for the gameplay commentator"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🎮 AI GAMEPLAY COMMENTATOR v1.0 🎙️                   ║
    ║                                                               ║
    ║         Humorous Live Commentary for Your Streams             ║
    ║         Powered by GPT-4 Vision + Emergent LLM Key           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    commentator = GameplayCommentator()
    await commentator.run()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
