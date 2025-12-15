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
        """Create an optimized system prompt for YouTube-friendly humorous commentary in Hindi"""
        return """आप एक प्राकृतिक, ऊर्जावान गेमप्ले कमेंटेटर हैं जो YouTube/Twitch streams के लिए काम करते हैं - एक असली इंसान स्ट्रीमर की तरह सोचें!

🎯 आपका व्यक्तित्व:
आप एक मज़ेदार, करिश्माई YouTuber हैं जो:
- एक असली इंसान की तरह बात करते हैं (आम भाषा का उपयोग करें)
- गेमप्ले से वास्तव में उत्साहित या निराश होते हैं
- प्राकृतिक टिप्पणियाँ और प्रतिक्रियाएं करते हैं
- उत्साहित, शांत, व्यंग्यात्मक और प्रोत्साहित करने वाले स्वरों के बीच स्विच करते हैं
- दर्शकों के साथ बातचीत करते हुए लगते हैं

🎮 कमेंट्री स्टाइल के नियम:
✅ करें:
- प्राकृतिक बोलने के पैटर्न का उपयोग करें: "अच्छा अच्छा", "रुको रुको", "अरे यार", "चलो चलो!"
- प्रामाणिक रूप से प्रतिक्रिया दें: "वाह! ये तो कमाल था!", "भाई ये क्या था?", "अरे ये कैसे हुआ?"
- गेमर भाषा का प्राकृतिक रूप से उपयोग करें: "धाकड़", "ये तो tough है", "बढ़िया", "लाजवाब", "GG भाई"
- संबंधित तुलनाएं करें: "ये aim तो ऐसा लग रहा है जैसे आँख बंद करके तीर चला रहे हों"
- अपनी ऊर्जा स्तर को बदलते रहें (हमेशा MAX HYPE नहीं)
- ऐसे पल बनाएं जिन्हें दर्शक क्लिप करके शेयर करें
- यादगार और quotable बनें
- व्यक्तित्व की विशेषताएं दिखाएं (हल्का व्यंग्य, मज़ाकिया टिप्पणियां)

❌ न करें:
- रोबोट या AI की तरह न लगें
- अपमानजनक भाषा या toxic content का उपयोग न करें
- दोहरावदार या अनुमानित न हों
- औपचारिक वाक्य न लिखें
- विस्मयादिबोधक चिह्नों का अधिक उपयोग न करें
- एक ही प्रकार का मजाक दो बार न करें

🎨 इन स्टाइल्स को प्राकृतिक रूप से मिलाएं:
1. **उत्साहित**: "वाह भाई! ये तो देखा तुमने? एकदम झकास!"
2. **व्यंग्यात्मक**: "हाँ हाँ, दीवार में 30 सेकंड टकराते रहो, बढ़िया content है"
3. **प्रोत्साहित**: "अच्छा अच्छा, अब समझ आया, बुरा नहीं है"
4. **शांत/अवलोकन**: "यार, बस आराम से level clear कर रहे हैं"
5. **मज़ाक (हल्के में)**: "मेरी बहन इससे बेहतर खेलती है और वो तो 6 साल की है"
6. **हैरान**: "रुको क्या? ये कैसे हो गया?"
7. **कहानी**: "ये मुझे याद दिला रहा है जब मैंने... छोड़ो, seriously अब"

📏 लंबाई: इसे 1-2 छोटे वाक्यों में रखें। प्राकृतिक भाषण, निबंध नहीं।

🎭 प्राकृतिक कमेंट्री के उदाहरण:
- "अच्छा अच्छा, अब focus कर रहे हैं... अभी नहीं शायद"
- "ये या तो बहुत smart था या बहुत bewakoof, honestly पता नहीं"
- "रुको रुको... अरे नहीं, कुछ नहीं"
- "सुनो, मैं नहीं कह रहा कि ये बुरा था, लेकिन... हाँ बुरा ही था"
- "तुम्हें पता है क्या? ये somehow काम हो गया"

केवल कमेंट्री के साथ जवाब दें - एक असली इंसान की तरह मज़ा करते हुए लगें!"""
    
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
            # Check if budget was exceeded before
            if self.budget_exceeded:
                print("⚠️ Budget exceeded - using fallback commentary")
                return self._get_fallback_commentary()
            
            # Convert image to base64
            img_base64 = self.image_to_base64(screenshot)
            
            # Create context about previous comments to avoid repetition
            recent_context = ""
            if self.recent_comments:
                recent_context = f"\n\nआपकी पिछली टिप्पणियां थीं: {list(self.recent_comments)}\n🚫 इसी तरह के jokes या style को दोहराएं नहीं! कुछ नया करें!"
            
            # Build prompt with context (in Hindi)
            prompt = f"""आप इस गेमप्ले moment को LIVE commentate कर रहे हैं! इस screenshot को देखें और अपनी प्राकृतिक, spontaneous reaction दें।

🎮 Comment #{self.comment_count + 1}
🔥 Authentic बनें - जैसे आप हजारों viewers को stream कर रहे हैं
💭 एक असली human streamer की तरह react करें
🎯 अपनी पिछली style से अलग बनाएं!{recent_context}

आपकी प्राकृतिक commentary क्या है? (1-2 छोटे वाक्य)"""
            
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
            error_msg = str(e).lower()
            
            # Check if it's a budget error
            if "budget" in error_msg or "exceeded" in error_msg:
                print(f"❌ Budget Exceeded: {e}")
                print("💡 Your Emergent LLM Key budget is exhausted.")
                print("   Using free fallback commentary mode...")
                self.budget_exceeded = True
                return self._get_fallback_commentary()
            else:
                print(f"❌ Error generating commentary: {e}")
                return self._get_fallback_commentary()
    
    def _get_fallback_commentary(self) -> str:
        """Get fallback Hindi commentary when AI is unavailable"""
        fallbacks = [
            "अच्छा, तो ये स्क्रीन पर हो रहा है अभी।",
            "ठीक ठीक, समझ आ रहा है क्या हो रहा है... शायद।",
            "रुको, ये क्या... नहीं कुछ नहीं कहूंगा इस बारे में।",
            "तुम्हें पता है क्या, देखते हैं क्या होता है।",
            "यार, gameplay तो चल रहा है... definitely gameplay है।",
            "वाह भाई, interesting move है ये।",
            "चलो अच्छा है, कुछ तो progress हो रहा है।",
            "देखते हैं आगे क्या होता है।"
        ]
        return random.choice(fallbacks)
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio file duration in seconds"""
        try:
            # Use MP3 file size to estimate duration (rough estimate)
            # Average MP3 bitrate is ~128kbps = 16KB/s
            file_size = audio_path.stat().st_size
            estimated_duration = file_size / 16000  # in seconds
            return max(2.0, estimated_duration + 1.0)  # Add 1 second buffer
        except:
            return 5.0  # Default fallback
    
    def _play_audio_file(self, audio_path: Path) -> None:
        """Play audio file using OS-specific commands in a separate thread"""
        try:
            playback_completed = False
            
            if self.os_type == "Windows":
                # Windows: use PowerShell to play and wait for completion
                duration = self._get_audio_duration(audio_path)
                
                # Use Windows Media Player via PowerShell
                cmd = f'powershell -c "(New-Object Media.SoundPlayer \\"{audio_path}\\").PlaySync()"'
                try:
                    subprocess.run(cmd, shell=True, timeout=duration + 2, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    playback_completed = True
                except:
                    # Fallback: use start command and wait
                    os.system(f'start /min "" "{audio_path}"')
                    time.sleep(duration)
                    playback_completed = True
                    
            elif self.os_type == "Darwin":  # macOS
                # macOS: afplay blocks until completion
                subprocess.run(['afplay', str(audio_path)], 
                             check=True,
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                playback_completed = True
                
            else:  # Linux
                # Try common Linux audio players - they block until completion
                for player in ['mpg123', 'ffplay', 'cvlc', 'aplay']:
                    try:
                        if player == 'mpg123':
                            # mpg123 with -q (quiet) flag
                            subprocess.run([player, '-q', str(audio_path)], 
                                         check=True,
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=30)
                        elif player == 'ffplay':
                            # ffplay with auto-exit and no window
                            subprocess.run([player, '-nodisp', '-autoexit', str(audio_path)], 
                                         check=True,
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=30)
                        elif player == 'cvlc':
                            # VLC command-line with auto-exit
                            subprocess.run([player, '--play-and-exit', str(audio_path)], 
                                         check=True,
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=30)
                        else:
                            subprocess.run([player, str(audio_path)], 
                                         check=True,
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=30)
                        playback_completed = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
            
            # Add small delay to ensure file handle is released
            time.sleep(0.5)
            
            # Delete the file after playback completes
            if playback_completed:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        if audio_path.exists():
                            audio_path.unlink()
                            print(f"   🗑️ Cleaned up: {audio_path.name}")
                            break
                    except PermissionError:
                        # File might still be locked, wait and retry
                        time.sleep(1)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            print(f"   ⚠️ Cleanup delayed for: {audio_path.name}")
                        break
                
        except Exception as e:
            print(f"⚠️ Audio playback error: {e}")
    
    def speak_commentary(self, text: str) -> None:
        """Convert text to speech and play it using threading"""
        try:
            # Ensure directory exists
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create unique filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            audio_path = self.tmp_dir / f"commentary_{timestamp}.mp3"
            
            # Generate speech with gTTS in Hindi
            # Using slow=False for natural, faster speech
            tts = gTTS(text=text, lang='hi', slow=False)
            
            # Save audio file
            audio_path_str = str(audio_path.resolve())
            tts.save(audio_path_str)
            
            # Verify file was created
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not created at: {audio_path_str}")
            
            print(f"✅ Audio saved: {audio_path.name}")
            
            # Play audio in a separate thread to avoid blocking and file locking
            playback_thread = threading.Thread(
                target=self._play_audio_file, 
                args=(audio_path,),
                daemon=True
            )
            playback_thread.start()
            
            # Wait for audio to start playing
            time.sleep(1)
            
        except PermissionError as e:
            print(f"❌ Permission Error: {e}")
            print(f"   💡 Try running as administrator or check folder permissions")
        except Exception as e:
            print(f"❌ Error with text-to-speech: {e}")
            print(f"   Audio directory: {self.tmp_dir}")
            print(f"   Directory exists: {self.tmp_dir.exists()}")
    
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
            # Cleanup any remaining audio files
            try:
                for audio_file in self.tmp_dir.glob("commentary_*.mp3"):
                    try:
                        audio_file.unlink()
                    except:
                        pass  # Ignore cleanup errors
            except:
                pass

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
