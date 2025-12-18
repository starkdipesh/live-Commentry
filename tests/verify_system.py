#!/usr/bin/env python3
"""
🧪 System Verification Suite
Tests the integrity of the Live Commentary System (Lightweight & Enhanced)
"""
import sys
import os
import asyncio
from pathlib import Path
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg):
    print(f"❌ FAIL: {msg}")
    return False

def print_skip(msg):
    print(f"⚠️ SKIP: {msg}")

async def run_tests():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 LIVE COMMENTARY SYSTEM - DIAGNOSTIC TEST               ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    all_passed = True

    # ---------------------------------------------------------
    # TEST 1: Dependency Import
    # ---------------------------------------------------------
    print("🔹 TEST 1: Checking Dependencies & Imports...")
    try:
        import mss
        from PIL import Image
        import edge_tts
        import pygame
        import requests
        from src.core.gameplay_commentator_lightweight import LightweightCommentator
        # Checks if we can import the new structure
        from src.processors.advanced_image_processor import AdvancedImageProcessor
        print_pass("All libraries imported successfully")
    except ImportError as e:
        print_fail(f"Dependency missing: {e}")
        all_passed = False
    except Exception as e:
        print_fail(f"Import error: {e}")
        all_passed = False

    # ---------------------------------------------------------
    # TEST 2: AI Model Connection (Ollama)
    # ---------------------------------------------------------
    print("\n🔹 TEST 2: Checking AI Model (Ollama)...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            if "llava:latest" in models:
                print_pass(f"Ollama running & 'llava:latest' found")
            else:
                print_fail("Ollama running but 'llava:latest' missing")
                all_passed = False
        else:
            print_fail("Ollama endpoint returned error")
            all_passed = False
    except requests.exceptions.ConnectionError:
        print_fail("Could not connect to Ollama (is it running?)")
        all_passed = False

    # ---------------------------------------------------------
    # TEST 3: Image Processing Pipeline
    # ---------------------------------------------------------
    print("\n🔹 TEST 3: Testing Image Processor...")
    try:
        # Create a dummy image
        img = Image.new('RGB', (1920, 1080), color = 'red')
        
        # Test Lightweight Logic (Simple Resize)
        resized_light = img.resize((512, 288))
        if resized_light.size == (512, 288):
             print_pass("Lightweight processing logic OK")
        
        # Test Enhanced Logic (Processor Class)
        processor = AdvancedImageProcessor(target_size=512)
        processed = processor.preprocess_for_vision_model(img, detect_motion=False)
        if processed.size[0] <= 512:
            print_pass("Enhanced Processor logic OK")
            
    except Exception as e:
        print_fail(f"Image processing failed: {e}")
        all_passed = False

    # ---------------------------------------------------------
    # TEST 4: Text-to-Speech Engine
    # ---------------------------------------------------------
    print("\n🔹 TEST 4: Testing TTS (Edge-TTS)...")
    try:
        output_file = Path("tests/test_audio.mp3")
        voice = "hi-IN-SwaraNeural"
        text = "Testing audio generation."
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_file))
        
        if output_file.exists() and output_file.stat().st_size > 0:
            print_pass("TTS Generated audio file successfully")
            output_file.unlink() # Cleanup
        else:
            print_fail("TTS failed to generate file")
            all_passed = False
    except Exception as e:
        print_fail(f"TTS Error: {e}")
        all_passed = False

    # ---------------------------------------------------------
    # TEST 5: Auto-Trainer Logic
    # ---------------------------------------------------------
    print("\n🔹 TEST 5: Checking Auto-Trainer...")
    try:
        from src.learning.auto_trainer import AutoTrainer
        trainer = AutoTrainer()
        if trainer.teacher_model == "llava:latest":
            print_pass("AutoTrainer initialized correct teacher model")
        else:
            print_fail("AutoTrainer configuration error")
            all_passed = False
    except Exception as e:
        print_fail(f"AutoTrainer module error: {e}")
        all_passed = False

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The system is solid.")
        print("   You can run './start.sh' with confidence.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the errors above.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
