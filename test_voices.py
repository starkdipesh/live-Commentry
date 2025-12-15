#!/usr/bin/env python3
"""
🎙️ Voice Testing & Configuration Tool
Test different Edge-TTS voices to find the most natural one
"""

import asyncio
import sys
from pathlib import Path
import subprocess
import os

try:
    import edge_tts
except ImportError:
    print("❌ edge-tts not installed!")
    print("   Install with: pip install edge-tts")
    sys.exit(1)

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame not available, will use system audio")

class VoiceTester:
    """Test and compare different voices"""
    
    def __init__(self):
        self.tmp_dir = Path(__file__).parent / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # Available Hindi voices in Edge-TTS (FREE)
        self.voices = {
            "hi-IN-SwaraNeural": "Female - Natural, Expressive, Warm",
            "hi-IN-MadhurNeural": "Male - Clear, Professional, Energetic",
        }
        
        # Test phrases
        self.test_phrases = [
            "वाह! ये तो कमाल का शॉट था!",
            "अरे यार, ये क्या हो गया?",
            "चलो भाई, अच्छा gameplay चल रहा है!",
            "धाकड़ move था ये तो!",
        ]
    
    async def test_voice(self, voice_name: str, text: str):
        """Test a specific voice with given text"""
        print(f"\n🎙️ Testing: {voice_name}")
        print(f"   Description: {self.voices.get(voice_name, 'Unknown')}")
        print(f"   Text: {text}")
        
        try:
            # Generate audio
            audio_file = self.tmp_dir / f"test_{voice_name.replace('-', '_')}.mp3"
            
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(str(audio_file))
            
            if not audio_file.exists():
                print(f"   ❌ Failed to generate audio")
                return False
            
            print(f"   ✅ Audio generated ({audio_file.stat().st_size} bytes)")
            
            # Play audio
            await self._play_audio(audio_file)
            
            # Cleanup
            try:
                audio_file.unlink()
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def _play_audio(self, audio_file: Path):
        """Play audio file"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                    
                print("   ✅ Playback complete")
            else:
                # System fallback
                os_type = os.uname().sysname if hasattr(os, 'uname') else 'Windows'
                
                if os_type == "Darwin":  # macOS
                    subprocess.run(['afplay', str(audio_file)])
                elif os_type == "Linux":
                    subprocess.run(['mpg123', '-q', str(audio_file)])
                else:  # Windows
                    os.system(f'start /min "" "{audio_file}"')
                    await asyncio.sleep(3)
                
                print("   ✅ Playback complete")
                
        except Exception as e:
            print(f"   ⚠️ Playback warning: {e}")
    
    async def test_all_voices(self):
        """Test all available voices"""
        print("\n" + "="*70)
        print("🎙️ EDGE-TTS VOICE TESTER (FREE Natural Voices)")
        print("="*70)
        print("\nTesting Hindi voices with sample phrases...")
        print("Listen carefully to choose the most natural voice!\n")
        
        for voice_name, description in self.voices.items():
            # Test with first phrase
            await self.test_voice(voice_name, self.test_phrases[0])
            
            # Wait a bit between voices
            await asyncio.sleep(1)
        
        print("\n" + "="*70)
        print("🎯 RECOMMENDATION")
        print("="*70)
        print("\n✨ Best voices for commentary:")
        print("   1. hi-IN-SwaraNeural  - Most natural, expressive female voice")
        print("   2. hi-IN-MadhurNeural - Clear, energetic male voice")
        print("\n💡 To change voice in gameplay_commentator_free.py:")
        print("   Edit line: self.current_voice = 'hi-IN-SwaraNeural'")
        print("   To your preferred voice from above\n")
    
    async def interactive_test(self):
        """Interactive voice testing"""
        print("\n" + "="*70)
        print("🎤 INTERACTIVE VOICE TEST")
        print("="*70)
        
        while True:
            print("\n📋 Available Voices:")
            for i, (voice, desc) in enumerate(self.voices.items(), 1):
                print(f"   {i}. {voice}")
                print(f"      {desc}")
            
            print(f"   {len(self.voices)+1}. Test all voices")
            print(f"   {len(self.voices)+2}. Exit")
            
            try:
                choice = input("\n👉 Select option: ").strip()
                
                if not choice.isdigit():
                    print("❌ Please enter a number")
                    continue
                
                choice = int(choice)
                
                if choice == len(self.voices) + 2:
                    print("\n👋 Goodbye!")
                    break
                elif choice == len(self.voices) + 1:
                    await self.test_all_voices()
                elif 1 <= choice <= len(self.voices):
                    voice_name = list(self.voices.keys())[choice - 1]
                    
                    # Get custom text
                    print("\n📝 Enter text to speak (or press Enter for default):")
                    custom_text = input("   Text: ").strip()
                    
                    if not custom_text:
                        custom_text = self.test_phrases[0]
                    
                    await self.test_voice(voice_name, custom_text)
                else:
                    print("❌ Invalid option")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    tester = VoiceTester()
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           🎙️ EDGE-TTS VOICE TESTER 🎧                        ║
    ║                                                               ║
    ║           Test Natural Hindi Voices (100% FREE)               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if we should run interactive or automated test
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        await tester.test_all_voices()
    else:
        await tester.interactive_test()

if __name__ == "__main__":
    asyncio.run(main())
