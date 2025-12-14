#!/usr/bin/env python3
"""
Quick test script to verify the gameplay commentator setup
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test if all required libraries are installed"""
    print("🧪 Testing imports...")
    
    try:
        import mss
        print("✅ mss (screen capture)")
    except ImportError as e:
        print(f"❌ mss: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (image processing)")
    except ImportError as e:
        print(f"❌ Pillow: {e}")
        return False
    
    try:
        from gtts import gTTS
        print("✅ gTTS (text-to-speech)")
    except ImportError as e:
        print(f"❌ gTTS: {e}")
        return False
    
    try:
        import pygame
        print("✅ pygame (audio playback)")
    except ImportError as e:
        print(f"❌ pygame: {e}")
        return False
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        print("✅ emergentintegrations (AI integration)")
    except ImportError as e:
        print(f"❌ emergentintegrations: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv (environment variables)")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
        return False
    
    return True

def test_env():
    """Test environment variables"""
    print("\n🧪 Testing environment variables...")
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv("EMERGENT_LLM_KEY")
    
    if api_key:
        print(f"✅ EMERGENT_LLM_KEY found: {api_key[:20]}...")
        return True
    else:
        print("❌ EMERGENT_LLM_KEY not found in .env")
        return False

def test_screen_capture():
    """Test screen capture functionality"""
    print("\n🧪 Testing screen capture...")
    
    try:
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            print(f"✅ Screen captured: {img.width}x{img.height}")
            return True
    except Exception as e:
        print(f"❌ Screen capture failed: {e}")
        return False

async def test_ai_connection():
    """Test AI connection with a simple message"""
    print("\n🧪 Testing AI connection...")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-35fA75602D104F9F64")
        
        chat = LlmChat(
            api_key=api_key,
            session_id="test-connection",
            system_message="You are a helpful assistant."
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(
            text="Say 'Connection successful!' and nothing else."
        ))
        
        print(f"✅ AI Response: {response}")
        return True
    except Exception as e:
        print(f"❌ AI connection failed: {e}")
        return False

def test_tts():
    """Test text-to-speech functionality"""
    print("\n🧪 Testing text-to-speech...")
    
    try:
        from gtts import gTTS
        import pygame
        from pathlib import Path
        
        # Generate test audio
        tts = gTTS(text="Testing text to speech", lang='en', slow=False)
        test_file = Path("/tmp/test_tts.mp3")
        tts.save(str(test_file))
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        print("✅ TTS generation successful")
        print("✅ pygame mixer initialized")
        
        # Cleanup
        pygame.mixer.quit()
        if test_file.exists():
            test_file.unlink()
        
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("🚀 GAMEPLAY COMMENTATOR - SYSTEM TEST")
    print("=" * 70)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Environment
    results.append(("Environment Variables", test_env()))
    
    # Test 3: Screen Capture
    results.append(("Screen Capture", test_screen_capture()))
    
    # Test 4: AI Connection
    results.append(("AI Connection", await test_ai_connection()))
    
    # Test 5: TTS
    results.append(("Text-to-Speech", test_tts()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! You're ready to run gameplay_commentator.py")
        print("\nRun: python3 /app/gameplay_commentator.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
