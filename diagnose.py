#!/usr/bin/env python3
"""
Saarthika System Diagnostic Tool
Helps identify why the system might not be working on different machines
"""
import sys
import subprocess

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_internet():
    """Check if internet is working"""
    print_header("1. Internet Connectivity Test")
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Internet connection is working")
        return True
    except Exception as e:
        print(f"❌ No internet connection: {e}")
        print("   → Saarthika needs internet to work!")
        return False

def check_groq_api():
    """Check if Groq API is reachable"""
    print_header("2. Groq API Connectivity Test")
    try:
        import requests
        response = requests.get("https://api.groq.com", timeout=10)
        print(f"✅ Groq servers are reachable (HTTP {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Groq API: {e}")
        print("   → Check firewall/proxy settings")
        return False

def check_api_key():
    """Check if API key is working"""
    print_header("3. API Key Validation Test")
    try:
        import requests
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        
        env_path = Path(__file__).resolve().parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        API_KEY = os.getenv('GROQ_API_KEY')
        
        if not API_KEY:
            print("❌ GROQ_API_KEY not found in .env file")
            print("   → Create .env with GROQ_API_KEY=your_key")
            return False
            
        print(f"   Using Key: ...{API_KEY[-8:]}")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            },
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ API key is valid and working")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            print("   → Get a new key from https://console.groq.com")
            return False
        else:
            print(f"⚠️ Unexpected response: HTTP {response.status_code}")
            print(f"   Details: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def check_dependencies():
    """Check if all Python packages are installed"""
    print_header("4. Python Dependencies Check")
    
    required = [
        'requests',
        'PIL',
        'mss',
        'cv2',
        'edge_tts',
        'pygame'
    ]
    
    all_ok = True
    for pkg in required:
        try:
            if pkg == 'PIL':
                import PIL
            elif pkg == 'cv2':
                import cv2
            else:
                __import__(pkg)
            print(f"✅ {pkg} is installed")
        except ImportError:
            if pkg in ['edge_tts', 'pygame']:
                print(f"⚠️  {pkg} is missing (TTS may not work)")
            else:
                print(f"❌ {pkg} is missing (CRITICAL)")
                all_ok = False
    
    return all_ok

def check_system_info():
    """Display system information"""
    print_header("5. System Information")
    
    import platform
    import os
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    if platform.system() == "Linux":
        session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
        print(f"Desktop Session: {session_type}")
        if session_type == 'wayland':
            print("⚠️  WAYLAND detected - Screen capture may not work in CLI mode")
            print("   → Use Web Dashboard OR switch to Xorg")

def run_full_test():
    """Run complete diagnostic"""
    print("\n" + "🔍" + "="*58 + "🔍")
    print("   SAARTHIKA SYSTEM DIAGNOSTIC TOOL")
    print("🔍" + "="*58 + "🔍\n")
    
    results = {
        "Internet": check_internet(),
        "Groq_API": check_groq_api(),
        "API_Key": check_api_key(),
        "Dependencies": check_dependencies()
    }
    
    check_system_info()
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:15} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL SYSTEMS GO! Saarthika should work perfectly.")
        print("\nTo start Saarthika:")
        print("  ./venv/bin/python3 serve.py")
    else:
        print("⚠️  ISSUES DETECTED. Fix the failures above.")
        print("\nCommon fixes:")
        print("• No Internet → Connect to WiFi")
        print("• API Key Fail → Check console.groq.com")
        print("• Missing Deps → Run: ./venv/bin/pip install -r requirements.txt")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user.")
        sys.exit(1)
