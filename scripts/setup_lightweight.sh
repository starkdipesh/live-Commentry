#!/bin/bash
# 🚀 Quick Setup for Low-Spec PC - 100% FREE (With Virtual Environment)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎮 Lightweight Commentary Setup - Low-Spec PC             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit

# Check Python
echo "📌 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"
echo ""

# Create Virtual Environment
echo "📌 Configuring Virtual Environment..."
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
else
    echo "venv already exists."
fi

# Activate venv
source venv/bin/activate
echo "✅ Virtual Environment Activated"

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Install minimal dependencies
echo "📦 Installing lightweight dependencies (minimal RAM usage)..."
if [ -f "requirements/requirements_lightweight.txt" ]; then
    pip install -r requirements/requirements_lightweight.txt
else
    echo "⚠️  Requirements file not found, installing manually..."
    pip install mss Pillow edge-tts pygame requests
fi
echo ""

# Check Ollama
echo "📌 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found."
    echo ""
    echo "Install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: https://ollama.ai"
    # Don't exit, might be remote or installed differently, but warn.
else
    echo "✅ Ollama: $(ollama --version)"
fi
echo ""

# Check if Ollama is running
echo "📌 Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama not running. Starting..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo "✅ Ollama started"
fi
echo ""

# Check for llava:latest
echo "📌 Checking for llava:latest model..."
# Determine if we can run ollama list
if command -v ollama &> /dev/null; then
    if ollama list | grep -q "llava:latest"; then
        echo "✅ llava:latest found (you already have this!)"
    else
        echo "⚠️  llava:latest not found."
        echo "📥 Downloading llava:latest (this may take 5-10 minutes)..."
        ollama pull llava:latest
    fi
else
    echo "⚠️  Skipping model check (Ollama not found in path)"
fi
echo ""

# Test lightweight system
echo "✅ Testing lightweight system..."
python3 -c "
from PIL import Image
print('   ✅ Image processing: OK')

try:
    import edge_tts
    print('   ✅ Text-to-speech: OK')
except:
    print('   ⚠️  edge-tts not installed')

try:
    import pygame
    print('   ✅ Audio playback: OK')
except:
    print('   ⚠️  pygame not installed')
" 2>&1
echo ""

# Show system info
echo "💻 Your System Configuration:"
echo "   RAM: $(free -h 2>/dev/null | awk '/^Mem:/ {print $2}' || echo 'N/A')"
echo "   CPU: $(nproc 2>/dev/null || echo 'N/A') cores"
echo ""

# Create a convenience runner
echo "#!/bin/bash" > start.sh
echo "source venv/bin/activate" >> start.sh
echo 'MODE=${1:-lightweight}' >> start.sh
echo 'python3 run.py "$MODE"' >> start.sh
chmod +x start.sh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE - Optimized for Low-Spec PC             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎮 To start lightweight commentary:"
echo ""
echo "   ./start.sh"
echo "   OR"
echo "   source venv/bin/activate"
echo "   python3 run.py lightweight"
echo ""
echo "📚 Read the guides in docs/"
echo "   • docs/guides/FREE_TRAINING_LOW_SPEC.md"
echo "   • docs/summaries/QUICK_REFERENCE.md"
echo ""
echo "🎯 Recommended next steps:"
echo "   1. Run: ./start.sh"
echo "   2. This weekend: Create custom Ollama Modelfile"
echo "   3. This month: Collect training data slowly"
echo ""
echo "Happy gaming! 🎮🎙️"
