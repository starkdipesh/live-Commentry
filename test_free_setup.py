#!/usr/bin/env python3
"""
Test script to verify FREE commentary setup
Run this before using the main commentator
"""

import sys

def test_imports():
    """Test if all required modules are installed"""
    print("\n═" * 70)
    print("🧪 Testing Python Imports...")
    print("═" * 70)
    
    modules = [
        ('mss', 'Screen Capture'),
        ('PIL', 'Image Processing'),
        ('pyttsx3', 'Text-to-Speech'),
        ('requests', 'HTTP Client')
    ]
    
    all_good = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"   ✅ {module:15s} - {description}")
        except ImportError:
            print(f"   ❌ {module:15s} - {description} (NOT INSTALLED)")
            all_good = False
    
    return all_good

def test_ollama():
    """Test Ollama connection and model availability"""
    print("\n═" * 70)
    print("🤖 Testing Ollama Connection...")
    print("═" * 70)
    
    import requests
    
    try:
        # Test connection
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            print("   ✅ Ollama service is running")
            
            # Check for LLaVA model
            data = response.json()
            models = data.get('models', [])
            model_names = [m['name'] for m in models]
            
            llava_found = any('llava' in name.lower() for name in model_names)
            
            if llava_found:
                print("   ✅ LLaVA model is installed")
                print(f"   📊 Available models: {', '.join(model_names)}")
                return True
            else:
                print("   ❌ LLaVA model NOT found")
                print("   📥 Run: ollama pull llava")
                return False
        else:
            print(f"   ❌ Ollama returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Ollama is NOT running")
        print("   🚀 Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_tts():
    """Test text-to-speech engine"""
    print("\n═" * 70)
    print("🔊 Testing Text-to-Speech...")
    print("═" * 70)
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        print("   ✅ TTS engine initialized")
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"   🎤 Available voices: {len(voices)}")
        
        # Check for Hindi voice
        hindi_voice = None
        for voice in voices:
            if 'hindi' in voice.name.lower():
                hindi_voice = voice.name
                break
        
        if hindi_voice:
            print(f"   ✅ Hindi voice found: {hindi_voice}")
        else:
            print("   ⚠️  No Hindi voice found (will use default)")
        
        # Test voice rate
        rate = engine.getProperty('rate')
        print(f"   📡 Speech rate: {rate} words/min")
        
        return True
        
    except Exception as e:
        print(f"   ❌ TTS Error: {e}")
        return False

def test_screen_capture():
    """Test screen capture capability"""
    print("\n═" * 70)
    print("📸 Testing Screen Capture...")
    print("═" * 70)
    
    try:
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"   ✅ Detected {len(monitors) - 1} monitor(s)")
            
            # Try to capture
            monitor = monitors[1]
            screenshot = sct.grab(monitor)
            print(f"   ✅ Captured {screenshot.width}x{screenshot.height} screenshot")
            
            # Convert to PIL
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            print(f"   ✅ Converted to PIL Image")
            
            return True
            
    except Exception as e:
        print(f"   ⚠️  Screen capture warning: {e}")
        print("   💡 This might fail in headless environments (normal)")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 FREE AI COMMENTARY SYSTEM - SETUP TEST")
    print("=" * 70)
    
    results = {
        "imports": test_imports(),
        "ollama": test_ollama(),
        "tts": test_tts(),
        "screen": test_screen_capture()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {test.capitalize():15s} - {'PASSED' if passed else 'FAILED'}")
    
    print("\n" + "═" * 70)
    
    if all(results.values()):
        print("✅ ALL TESTS PASSED!")
        print("═" * 70)
        print("\n🎉 Your system is ready!")
        print("\n🚀 Run: python3 gameplay_commentator_free.py")
        print("\n")
        return 0
    elif results["imports"] and results["ollama"] and results["tts"]:
        print("⚠️  CORE TESTS PASSED (Screen capture may fail in containers)")
        print("═" * 70)
        print("\n💡 System should work on local machine with display")
        print("\n🚀 Run: python3 gameplay_commentator_free.py")
        print("\n")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("═" * 70)
        print("\n🔧 Fix the failed tests before running the commentator")
        print("\n📚 Check FREE_COMMENTARY_README.md for troubleshooting")
        print("\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
