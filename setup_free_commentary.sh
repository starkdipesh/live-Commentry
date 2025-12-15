#!/bin/bash

# 🎮 FREE AI Gameplay Commentary - Automated Setup Script
# This script sets up everything needed for FREE local AI commentary

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║       🎮 FREE AI GAMEPLAY COMMENTATOR SETUP 🎙️               ║"
echo "║                                                               ║"
echo "║       Setting up Ollama + LLaVA + Natural Voice               ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🖥️  Detected OS: $MACHINE"
echo ""

# Step 1: Check Python
echo "📋 Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION found"
else
    echo "   ❌ Python 3 not found!"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi
echo ""

# Step 2: Install Python dependencies
echo "📦 Step 2: Installing Python dependencies..."
if [ -f "requirements_free.txt" ]; then
    python3 -m pip install -r requirements_free.txt
    echo "   ✅ Python dependencies installed"
else
    echo "   ⚠️  requirements_free.txt not found, installing manually..."
    python3 -m pip install mss Pillow pyttsx3 requests
    echo "   ✅ Core dependencies installed"
fi
echo ""

# Step 3: Check/Install Ollama
echo "🤖 Step 3: Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 || echo "installed")
    echo "   ✅ Ollama is installed: $OLLAMA_VERSION"
else
    echo "   ⚠️  Ollama not found!"
    echo ""
    echo "   📥 Please install Ollama:"
    if [ "$MACHINE" = "Mac" ]; then
        echo "      brew install ollama"
        echo "      OR download from: https://ollama.ai/download"
    elif [ "$MACHINE" = "Linux" ]; then
        echo "      curl -fsSL https://ollama.ai/install.sh | sh"
    elif [ "$MACHINE" = "Windows" ]; then
        echo "      Download from: https://ollama.ai/download"
    fi
    echo ""
    echo "   After installing Ollama, run this script again!"
    exit 1
fi
echo ""

# Step 4: Check if Ollama is running
echo "🔌 Step 4: Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama service is running"
else
    echo "   ⚠️  Ollama service is not running"
    echo ""
    echo "   Please start Ollama in a separate terminal:"
    echo "      ollama serve"
    echo ""
    echo "   (Keep that terminal open while using the commentator)"
    echo ""
    read -p "   Press Enter after starting Ollama..."
    
    # Check again
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✅ Ollama service is now running!"
    else
        echo "   ❌ Still can't connect to Ollama"
        echo "   Make sure 'ollama serve' is running in another terminal"
        exit 1
    fi
fi
echo ""

# Step 5: Pull LLaVA model
echo "📥 Step 5: Downloading LLaVA vision model..."
echo "   (This may take a few minutes on first run - ~4.7GB download)"
echo ""

if ollama list | grep -q "llava"; then
    echo "   ✅ LLaVA model already installed"
else
    echo "   ⏳ Pulling llava:latest..."
    ollama pull llava:latest
    
    if [ $? -eq 0 ]; then
        echo "   ✅ LLaVA model downloaded successfully!"
    else
        echo "   ❌ Failed to download LLaVA model"
        echo "   Try manually: ollama pull llava"
        exit 1
    fi
fi
echo ""

# Step 6: Test TTS
echo "🔊 Step 6: Testing Text-to-Speech..."
python3 -c "import pyttsx3; engine = pyttsx3.init(); print('   ✅ TTS engine initialized')"
if [ $? -eq 0 ]; then
    echo "   ✅ Voice synthesis ready"
else
    echo "   ⚠️  TTS warning (will still work, just might be silent)"
    if [ "$MACHINE" = "Linux" ]; then
        echo "   Install espeak if needed: sudo apt-get install espeak"
    fi
fi
echo ""

# Step 7: Final check
echo "🎯 Step 7: Running system test..."
python3 << 'PYTHON_TEST'
import sys
try:
    import mss
    import PIL
    import pyttsx3
    import requests
    print("   ✅ All imports successful")
    
    # Test Ollama connection
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama connection verified")
    else:
        print("   ⚠️  Ollama connection issue")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo "   ✅ System test passed!"
else
    echo "   ❌ System test failed"
    exit 1
fi
echo ""

# Success!
echo "═══════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🎮 Your FREE AI Gameplay Commentator is ready!"
echo ""
echo "📋 To use:"
echo "   1. Make sure Ollama is running: ollama serve (in separate terminal)"
echo "   2. Run the commentator: python3 gameplay_commentator_free.py"
echo "   3. Play your game and enjoy FREE AI commentary!"
echo ""
echo "💡 Tips:"
echo "   - No internet needed after setup"
echo "   - No API costs ever"
echo "   - Works completely offline"
echo "   - Natural voice with emotion"
echo ""
echo "🎉 Happy Gaming!"
echo "═══════════════════════════════════════════════════════════════"
