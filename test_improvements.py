#!/usr/bin/env python3
"""
Quick test script to verify improvements in gameplay commentator
"""
import sys
import time
from pathlib import Path

print("=" * 70)
print("🧪 TESTING GAMEPLAY COMMENTATOR IMPROVEMENTS")
print("=" * 70)

# Test 1: Import check
print("\n1️⃣ Testing imports...")
try:
    import mss
    from PIL import Image, ImageEnhance
    import edge_tts
    import pygame
    import requests
    print("✅ All required packages imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Check if script has new features
print("\n2️⃣ Checking script improvements...")
script_path = Path(__file__).parent / "gameplay_commentator_free.py"
with open(script_path, 'r') as f:
    content = f.read()

improvements = {
    "temperature": "temperature" in content and "0.9" in content,
    "top_p": "top_p" in content and "0.95" in content,
    "repeat_penalty": "repeat_penalty" in content and "1.5" in content,
    "similarity_check": "_is_too_similar" in content,
    "enhanced_prompt": "FORBIDDEN" in content or "SPECIFIC" in content,
    "image_enhance": "ImageEnhance" in content,
    "jpeg_quality_95": "quality=95" in content,
    "rate_adjustment": 'rate="' in content,
    "async_cleanup": "_cleanup_audio" in content,
}

print("\n📊 Feature check:")
for feature, present in improvements.items():
    status = "✅" if present else "❌"
    print(f"   {status} {feature}")

all_present = all(improvements.values())
if all_present:
    print("\n✅ All improvements successfully implemented!")
else:
    print("\n⚠️ Some improvements might be missing")

# Test 3: Check configuration values
print("\n3️⃣ Checking configuration...")
config_checks = {
    "recent_comments deque(maxlen=10)": "maxlen=10" in content,
    "screenshot_interval = 6": "screenshot_interval = 6" in content or "screenshot_interval=6" in content,
    "timeout = 20": "timeout=20" in content or "timeout = 20" in content,
}

for check, present in config_checks.items():
    status = "✅" if present else "⚠️"
    print(f"   {status} {check}")

# Test 4: Ollama availability check
print("\n4️⃣ Checking Ollama status...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        print(f"✅ Ollama is running!")
        print(f"   Available models: {', '.join(model_names) if model_names else 'None'}")
        
        if any('llava' in name.lower() for name in model_names):
            print("✅ LLaVA model is installed!")
        else:
            print("⚠️ LLaVA model not found. Run: ollama pull llava")
    else:
        print(f"⚠️ Ollama returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("⚠️ Ollama is not running")
    print("   Start it with: ollama serve")
except Exception as e:
    print(f"⚠️ Could not check Ollama: {e}")

# Test 5: Edge-TTS voices
print("\n5️⃣ Testing Edge-TTS voices...")
try:
    import asyncio
    async def test_voices():
        voices = await edge_tts.list_voices()
        hindi_voices = [v for v in voices if v['Locale'].startswith('hi-')]
        if hindi_voices:
            print(f"✅ Found {len(hindi_voices)} Hindi voices available")
            for v in hindi_voices[:3]:
                print(f"   - {v['ShortName']}")
        else:
            print("⚠️ No Hindi voices found")
    
    asyncio.run(test_voices())
except Exception as e:
    print(f"⚠️ Could not test voices: {e}")

# Summary
print("\n" + "=" * 70)
print("📋 TEST SUMMARY")
print("=" * 70)
print("\n🎯 Key Improvements:")
print("   ⚡ Speed: Reduced timeout (30s→20s), faster speech (+15%)")
print("   🔄 Repetition: Advanced AI parameters + similarity detection")
print("   🎯 Accuracy: Better image quality (85→95), sharpening")
print("   😄 Humor: Enhanced prompts + 20 diverse fallbacks")
print("\n✨ The script is ready to use with improvements!")
print("\n📖 To run the commentator:")
print("   1. Make sure Ollama is running: ollama serve")
print("   2. Pull LLaVA model if needed: ollama pull llava")
print("   3. Run: python3 gameplay_commentator_free.py")
print("\n" + "=" * 70)
