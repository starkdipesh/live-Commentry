#!/usr/bin/env python3
"""
Windows Permission Diagnostic Tool
Tests if tmp folder can be created and used on Windows
"""

import sys
from pathlib import Path
import tempfile

def test_windows_permissions():
    print("="*70)
    print("🪟 WINDOWS PERMISSION DIAGNOSTIC TOOL")
    print("="*70)
    print("\nChecking if your system can create and write audio files...\n")
    
    results = []
    
    # Test 1: Current Directory
    print("📁 Test 1: Current Directory")
    try:
        current_dir = Path.cwd()
        print(f"   Location: {current_dir}")
        test_file = current_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Can write to current directory")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Cannot write: {e}")
        results.append(False)
    
    # Test 2: Local tmp Folder
    print("\n📁 Test 2: Local tmp Folder")
    try:
        tmp_dir = Path("tmp")
        print(f"   Location: {tmp_dir.resolve()}")
        
        # Try to create
        tmp_dir.mkdir(exist_ok=True)
        print("   ✅ tmp folder created/exists")
        
        # Try to write
        test_file = tmp_dir / "test_permission.txt"
        test_file.write_text("test")
        print("   ✅ Can write to tmp folder")
        
        # Try to delete
        test_file.unlink()
        print("   ✅ Can delete files")
        
        results.append(True)
    except Exception as e:
        print(f"   ❌ Local tmp failed: {e}")
        results.append(False)
    
    # Test 3: System Temp
    print("\n📁 Test 3: System Temp Folder")
    try:
        system_tmp = Path(tempfile.gettempdir())
        print(f"   Location: {system_tmp}")
        
        test_file = system_tmp / "commentary_test.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ System temp folder works")
        results.append(True)
    except Exception as e:
        print(f"   ❌ System temp failed: {e}")
        results.append(False)
    
    # Test 4: Audio Generation (if gtts available)
    print("\n🔊 Test 4: Audio Generation")
    try:
        from gtts import gTTS
        print("   ✅ gTTS library installed")
        
        # Try in tmp folder first
        try:
            tmp_dir = Path("tmp")
            tmp_dir.mkdir(exist_ok=True)
            audio_path = tmp_dir / "test_audio.mp3"
            
            tts = gTTS(text="Testing Windows audio", lang='en')
            tts.save(str(audio_path.resolve()))
            
            if audio_path.exists():
                size = audio_path.stat().st_size
                print(f"   ✅ Audio generated in local tmp: {size} bytes")
                audio_path.unlink()
                results.append(True)
            else:
                raise FileNotFoundError("Audio file not created")
                
        except Exception as e1:
            print(f"   ⚠️  Local tmp failed: {e1}")
            print("   Trying system temp...")
            
            # Fallback to system temp
            system_tmp = Path(tempfile.gettempdir())
            audio_path = system_tmp / "test_audio.mp3"
            
            tts = gTTS(text="Testing Windows audio", lang='en')
            tts.save(str(audio_path.resolve()))
            
            if audio_path.exists():
                size = audio_path.stat().st_size
                print(f"   ✅ Audio generated in system temp: {size} bytes")
                audio_path.unlink()
                results.append(True)
            else:
                raise FileNotFoundError("Audio file not created in system temp either")
                
    except ImportError:
        print("   ⚠️  gTTS not installed (run: pip install gtts)")
        results.append(None)
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")
        results.append(False)
    
    # Test 5: Path Resolution
    print("\n🛣️  Test 5: Path Handling")
    try:
        test_path = Path("tmp") / "test.mp3"
        resolved = test_path.resolve()
        print(f"   Original: tmp/test.mp3")
        print(f"   Resolved: {resolved}")
        print(f"   ✅ Path resolution works")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Path error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*70)
    
    test_names = [
        "Current Directory Write",
        "Local tmp Folder",
        "System Temp Folder",
        "Audio Generation",
        "Path Resolution"
    ]
    
    for name, result in zip(test_names, results):
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"{name:.<45} {status}")
    
    print("="*70)
    
    # Recommendations
    passed_count = sum(1 for r in results if r is True)
    failed_count = sum(1 for r in results if r is False)
    
    print("\n💡 RECOMMENDATIONS:\n")
    
    if failed_count == 0:
        print("✅ ALL TESTS PASSED!")
        print("   Your system is ready to run the commentary system.")
        print("\n🚀 Run: python gameplay_commentator.py")
        
    elif results[1] is False:  # Local tmp failed
        print("⚠️  Local tmp folder has permission issues.")
        print("\n🔧 SOLUTION OPTIONS:")
        print("   1. Run as Administrator")
        print("   2. Manually create tmp folder:")
        print("      - Windows Explorer: Right-click → New → Folder → 'tmp'")
        print("      - Command: mkdir tmp")
        print("   3. The script will auto-fallback to system temp (C:\\Users\\...\\AppData\\Local\\Temp)")
        print("\n   The auto-fallback should work fine! Just ignore the warning.")
        
    elif results[3] is False:  # Audio generation failed
        print("⚠️  Audio generation failed in both locations.")
        print("\n🔧 SOLUTIONS:")
        print("   1. Install dependencies: pip install gtts")
        print("   2. Check antivirus isn't blocking Python")
        print("   3. Try running as Administrator")
        
    else:
        print("⚠️  Some tests failed but system might still work.")
        print("   The script has automatic fallbacks built-in.")
        
    print("\n📖 For detailed help, see: WINDOWS_FIX.md")
    print("="*70)
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = test_windows_permissions()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
