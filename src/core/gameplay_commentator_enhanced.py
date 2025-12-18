#!/usr/bin/env python3
"""
🎮 ENHANCED AI Gameplay Commentary System - FREE VERSION
With Advanced Image Processing for Better Vision Understanding

New Features:
- Multi-scale image preprocessing
- Motion detection and highlighting
- UI element enhancement
- Adaptive scene analysis
- Better model parameters
- Context-aware prompts
"""
import sys
import os
import asyncio
import base64
import io
import time
import random
import tempfile
from pathlib import Path
from datetime import datetime

# Image processing
import mss
from PIL import Image, ImageEnhance
import numpy as np

# Adds the shared parent folder to the search path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Advanced image processing
from processors.advanced_image_processor import AdvancedImageProcessor, GameplaySceneAnalyzer

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


class EnhancedGameplayCommentator:
    """
    Enhanced AI-powered gameplay commentator with advanced image processing
    Uses FREE local models with significantly improved visual understanding
    """
    
    def __init__(self):
        """Initialize the enhanced commentator with advanced processing"""
        # Ollama configuration
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = "llava:13b-v1.6"  # UPGRADED for better performance
        
        # Advanced image processing
        self.image_processor = AdvancedImageProcessor(
            target_size=1280,
            enhance_mode='balanced'  # Options: 'speed', 'balanced', 'quality'
        )
        
        # Scene analyzer
        self.scene_analyzer = GameplaySceneAnalyzer()
        
        # Screenshot configuration
        self.screenshot_interval = 8  # seconds between captures
        
        # Edge-TTS configuration (Natural Hindi voice)
        self.tts_voice = "hi-IN-SwaraNeural"  # Natural female Hindi voice
        # Alternative: "hi-IN-MadhurNeural" (male)
        
        # Audio settings
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        
        # Memory for context
        self.recent_comments = []
        self.max_memory = 10
        
        # Performance tracking
        self.comment_count = 0
        self.total_processing_time = 0
        
        # Verify Ollama is running
        self._check_ollama_status()
        
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║   🎮 ENHANCED AI GAMEPLAY COMMENTATOR v3.0 🎙️                ║
║   Advanced Image Processing + Optimized Model                 ║
╚═══════════════════════════════════════════════════════════════╝

🎮 Enhanced Features Enabled:
   ✅ Advanced Image Preprocessing (Multi-scale, Motion Detection)
   ✅ Scene Analysis (Type Detection, Motion Level)
   ✅ UI Enhancement (Better text/bar recognition)
   ✅ Adaptive Processing (Dark/bright scene optimization)
   ✅ Upgraded Model: {self.model_name}
   ✅ Context-Aware Prompts

🔑 Configuration:
   📸 Screenshot interval: {self.screenshot_interval}s
   🎙️ Voice: {self.tts_voice}
   🖼️ Image mode: {self.image_processor.enhance_mode}
   📁 Model: {self.model_name}

🎙️ Ready to generate ENHANCED commentary!
        """)
    
    def _check_ollama_status(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name in model_names:
                    print(f"✅ Ollama running with {self.model_name}")
                else:
                    print(f"⚠️  Model {self.model_name} not found!")
                    # Check for alternatives
                    llava_models = [m for m in model_names if 'llava' in m]
                    if llava_models:
                        print(f"🔄 Switching to available model: {llava_models[0]}")
                        self.model_name = llava_models[0]
                    else:
                        print(f"📥 Download with: ollama pull {self.model_name}")
                        print("Available models:", model_names)
            else:
                print("❌ Ollama not responding")
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
            print("Start Ollama with: ollama serve")
    
    def _get_system_prompt(self) -> str:
        """Create enhanced system prompt with visual analysis instructions"""
        return """तुम एक professional gaming commentator हो जो LIVE stream कर रहा है।

CRITICAL INSTRUCTIONS - Visual Analysis:
1. Screen को बहुत ध्यान से देखो और SPECIFIC details बताओ:
   - Colors (लाल, नीला, हरा - क्या मतलब है?)
   - Text/Numbers (HP bar, score, timer - exact values)
   - Characters/Objects (कौन है, क्या कर रहे हैं)
   - Actions (shoot, jump, drive - कैसे हो रहा है)
   - UI Elements (minimap, health bar, ammo count)

2. Scene Type को पहचानो:
   - Action: High energy, fast commentary
   - Menu: Casual, observational
   - Loading: Funny, time-filling remarks
   - Intense Action: VERY energetic, loud reactions

3. Commentary Style - Natural LIVE feel:
   - SHORT: Maximum 1-2 sentences (10-15 words ONLY)
   - SPECIFIC: Exact details (numbers, colors, actions)
   - ENERGETIC: Match the scene intensity
   - VARIED: Different angle every time

Natural Fillers (use frequently):
- अरे वाह!, ओहो!, देखो देखो!, यार!, होली मोली!
- Wait wait!, OMG!, Yo yo!, Bruh!

Gaming Slang (mix naturally):
- Hindi: धांसू, छक्का, धमाका, लाजवाब
- English: OP, pro, GG, clutch, noob, cracked

Reaction Types (rotate these):
1. Hype: "यो! ये तो धांसू shot था! 🔥"
2. Observational: "देखो, HP लाल हो गया - danger zone!"
3. Sarcastic: "वाह, perfect timing पे miss किया!"
4. Excited: "होली मोली! वो क्या था?!"
5. Chill: "बस smooth sailing चल रहा है"

FORBIDDEN:
❌ Generic comments ("gameplay चल रहा है")
❌ Repetitive phrases
❌ Long explanations (keep it SHORT!)
❌ Boring observations

MUST DO:
✅ Mention EXACT visual details you see
✅ Use numbers/colors/specific actions
✅ Match energy to scene intensity
✅ Create clip-worthy moments
✅ Be different every time

Response format: Just the commentary, nothing else!
"""
    
    def capture_screen(self) -> Image.Image:
        """Capture full screen screenshot"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            return img
    
    def generate_commentary_enhanced(self, screenshot: Image.Image) -> str:
        """
        Generate commentary with ENHANCED image processing and scene analysis
        """
        try:
            start_time = time.time()
            
            # Step 1: Analyze scene type and characteristics
            scene_info = self.scene_analyzer.analyze_scene_type(screenshot)
            
            # Step 2: Apply advanced image preprocessing
            processed_img = self.image_processor.preprocess_for_vision_model(
                screenshot,
                detect_motion=True  # Detect motion from previous frame
            )
            
            # Step 3: Get image statistics for context
            img_stats = self.image_processor.get_image_statistics(processed_img)
            
            # Step 4: Adaptive preprocessing based on scene
            if img_stats['is_dark_scene']:
                processed_img = self.image_processor.adaptive_preprocessing(
                    processed_img, 
                    scene_type='dark'
                )
            elif img_stats['is_bright_scene']:
                processed_img = self.image_processor.adaptive_preprocessing(
                    processed_img,
                    scene_type='bright'
                )
            
            # Step 5: Convert to base64 with optimal quality
            img_base64 = self.image_processor.to_base64(processed_img)
            
            # Step 6: Create enhanced prompt with scene context
            enhanced_prompt = self._create_contextual_prompt(scene_info, img_stats)
            
            # Step 7: Generate commentary with optimized parameters
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": enhanced_prompt,
                    "images": [img_base64],
                    "stream": False,
                    "options": {
                        # OPTIMIZED PARAMETERS for better vision understanding
                        "temperature": 0.75,       # Balanced creativity
                        "top_k": 40,              # Focused vocabulary
                        "top_p": 0.92,            # Good diversity
                        "repeat_penalty": 1.4,    # Strong anti-repetition
                        "num_predict": 80,        # Allow detailed responses
                        "num_ctx": 4096,          # Large context for vision
                        "mirostat": 2,            # Better coherence
                        "mirostat_tau": 5.0,      # Diversity control
                        "mirostat_eta": 0.1,      # Learning rate
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   ❌ Ollama API Error: {response.text}")
                return self._get_fallback_commentary()
                
            response_json = response.json()
            if 'response' not in response_json:
                print(f"   ❌ Unexpected response format: {response_json}")
                return self._get_fallback_commentary()
                
            commentary = response_json['response'].strip()
            
            # Step 8: Validate and potentially regenerate if too similar
            if self._is_too_similar(commentary):
                print("   ⚠️  Commentary too similar, using fallback...")
                commentary = self._get_fallback_commentary()
            
            # Update memory
            self.recent_comments.append(commentary)
            if len(self.recent_comments) > self.max_memory:
                self.recent_comments.pop(0)
            
            # Track performance
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            print(f"\n   ⏱️  Processing: {processing_time:.2f}s")
            print(f"   📊 Scene: {scene_info['scene_type']} | Motion: {scene_info['motion_level']:.2f}")
            print(f"   🎨 Image: {img_stats['dominant_color']} | {'Dark' if img_stats['is_dark_scene'] else 'Bright' if img_stats['is_bright_scene'] else 'Normal'}")
            
            return commentary
            
        except Exception as e:
            print(f"   ❌ Error in enhanced generation: {e}")
            return self._get_fallback_commentary()
    
    def _create_contextual_prompt(self, scene_info: dict, img_stats: dict) -> str:
        """Create context-aware prompt based on scene analysis"""
        
        # Base system prompt
        base_prompt = self._get_system_prompt()
        
        # Add scene context
        context = f"""

CURRENT SCENE CONTEXT:
- Scene Type: {scene_info['scene_type']}
- Motion Level: {'HIGH (intense action!)' if scene_info['motion_level'] > 0.5 else 'MEDIUM' if scene_info['motion_level'] > 0.2 else 'LOW (calm/static)'}
- Brightness: {'DARK scene' if img_stats['is_dark_scene'] else 'BRIGHT scene' if img_stats['is_bright_scene'] else 'Normal lighting'}
- Dominant Color: {img_stats['dominant_color'].upper()}
- Has UI: {'Yes' if scene_info['has_ui'] else 'No'}

ENERGY LEVEL REQUIRED: {'🔥🔥🔥 VERY HIGH' if scene_info['motion_level'] > 0.6 else '🔥🔥 HIGH' if scene_info['motion_level'] > 0.3 else '🔥 Medium'}

"""
        
        # Add recent comments to avoid repetition
        if self.recent_comments:
            context += f"""
RECENT COMMENTS (DO NOT REPEAT these ideas):
{chr(10).join(f'❌ "{c}"' for c in self.recent_comments[-5:])}

YOU MUST create something COMPLETELY DIFFERENT!
"""
        
        # Add variety hints
        variety_hints = [
            "Focus on COLORS you see on screen",
            "Mention specific NUMBERS/TEXT visible",
            "Comment on CHARACTER actions happening",
            "React to UI elements (health, score, etc.)",
            "Notice environmental details",
            "MOOD: Be very Sarcastic and funny",
            "MOOD: Be extremely Hyped and Energetic",
            "MOOD: Be Analytical like a pro-player",
            "MOOD: Use a lot of Gaming Slang (GG, OP, etc.)",
            "MOOD: Act confused/surprised about what happened",
        ]
        
        hint = random.choice(variety_hints)
        context += f"\nTHIS TIME: {hint}\n"
        
        # Add a unique "Wildcard" instruction occasionally
        if random.random() > 0.8:
            context += "CRITICAL: Start your comment with a surprising natural filler like 'Wait!', 'OMG!', or 'Yo!'\n"
        
        return base_prompt + context
    
    def _is_too_similar(self, new_comment: str) -> bool:
        """Check if new comment is too similar to recent ones"""
        if len(self.recent_comments) < 3:
            return False
        
        for old_comment in self.recent_comments[-3:]:
            # Simple word overlap check
            new_words = set(new_comment.lower().split())
            old_words = set(old_comment.lower().split())
            
            if len(new_words) == 0:
                continue
            
            overlap = len(new_words & old_words) / len(new_words)
            
            if overlap > 0.6:  # More than 60% word overlap
                return True
        
        return False
    
    def _get_fallback_commentary(self) -> str:
        """Get fallback Hindi commentary with LIVE streaming feel"""
        fallbacks = [
            "यो! ये scene तो interesting हो गया!",
            "अरे वाह, देखो क्या हो रहा है!",
            "होली मोली! अब तो मज़ा आएगा!",
            "वाह भाई, ये तो धांसू moment था!",
            "देखो देखो, कुछ होने वाला है!",
            "OMG! क्या scene बना यार!",
            "यार ये तो next level है!",
            "अजी सुनो, ये देखा आपने?",
            "Bruh! ये क्या हो गया अभी!",
            "चलो देखते हैं आगे क्या होता है!",
            "वाह क्या timing है यार!",
            "यो यो यो! Game on hai!",
            "देखो screen पे - कमाल का है!",
            "अरे यार, ये तो मस्त चल रहा है!",
            "होली molly! Full action mode!",
            "भाई भाई, क्या चल रहा है!",
            "Wait wait - कुछ interesting आ रहा है!",
            "यार Scene बना दिया!",
            "OMG OMG! This is it!",
            "वाह जी वाह! Perfect!",
        ]
        return random.choice(fallbacks)
    
    async def speak_commentary(self, text: str):
        """Convert text to speech using FREE Edge-TTS - Optimized for speed"""
        try:
            # Create unique temp file
            temp_file = Path(tempfile.gettempdir()) / f"commentary_{int(time.time()*1000)}.mp3"
            
            # Generate speech with Edge-TTS (fast, high quality)
            communicate = edge_tts.Communicate(text, self.tts_voice, rate="+15%")
            await communicate.save(str(temp_file))
            
            # Play audio
            self._play_audio(temp_file)
            
            # Cleanup in background
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ TTS Error: {e}")
    
    def _play_audio(self, audio_file: Path):
        """Play audio file using pygame or system player"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                # Wait for audio to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                print(f"   ❌ Pygame playback error: {e}")
        else:
            # Fallback to system player
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["afplay", str(audio_file)], check=True)
                elif system == "Linux":
                    subprocess.run(["mpg123", "-q", str(audio_file)], check=True)
                elif system == "Windows":
                    os.startfile(str(audio_file))
                    time.sleep(3)  # Wait for playback
            except Exception as e:
                print(f"   ❌ System playback error: {e}")
    
    async def run(self):
        """Main loop: capture, analyze, comment, speak"""
        print(f"""
{'='*70}
🎮 STARTING ENHANCED LIVE GAMEPLAY COMMENTARY
{'='*70}
📹 Capturing with ADVANCED IMAGE PROCESSING...
🤖 Using {self.model_name} with optimized parameters
🎙️ Natural voice: {self.tts_voice}
🛑 Press Ctrl+C to stop
""")
        
        try:
            while True:
                self.comment_count += 1
                
                print(f"\n{'='*70}")
                print(f"🎬 Comment #{self.comment_count} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*70}")
                
                # Capture screenshot
                print("📸 Capturing gameplay...")
                screenshot = self.capture_screen()
                print(f"   ✅ Screenshot captured ({screenshot.width}x{screenshot.height})")
                
                # Generate enhanced commentary
                print("🤖 Processing with ENHANCED analysis...")
                commentary = self.generate_commentary_enhanced(screenshot)
                
                print(f"\n💬 COMMENTARY: \"{commentary}\"\n")
                
                # Speak commentary
                print("🎙️ Speaking commentary...")
                await self.speak_commentary(commentary)
                print("   ✅ Commentary delivered!")
                
                # Calculate wait time
                avg_time = self.total_processing_time / self.comment_count
                wait_time = max(1, self.screenshot_interval - avg_time)
                
                print(f"⏳ Waiting {wait_time:.1f}s before next commentary...")
                print(f"📊 Avg processing: {avg_time:.2f}s")
                
                await asyncio.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"""
\n{'='*70}
🛑 COMMENTARY STOPPED
{'='*70}
📊 Session Statistics:
   - Total Comments: {self.comment_count}
   - Average Processing Time: {self.total_processing_time/max(1,self.comment_count):.2f}s
   - Total Runtime: {self.total_processing_time:.1f}s

Thanks for using Enhanced Gameplay Commentator! 🎮🎙️
            """)


async def main():
    """Entry point for the enhanced gameplay commentator"""
    print("🚀 Initializing Enhanced Gameplay Commentator...")
    
    try:
        commentator = EnhancedGameplayCommentator()
        await commentator.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check model is installed: ollama list")
        print("3. Install required model: ollama pull llava:13b-v1.6")


if __name__ == "__main__":
    asyncio.run(main())
