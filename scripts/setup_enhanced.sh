#!/bin/bash
# 🚀 Quick Setup Script for Enhanced Commentary System

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎮 Enhanced Gameplay Commentary - Quick Setup             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "📌 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing enhanced dependencies..."
pip install -r requirements_enhanced.txt
echo ""

# Check Ollama
echo "📌 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found."
    echo ""
    echo "Install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: Download from https://ollama.ai"
    exit 1
fi
echo "✅ Ollama found: $(ollama --version)"
echo ""

# Check if Ollama is running
echo "📌 Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama not running. Starting in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✅ Ollama started"
fi
echo ""

# Pull upgraded model
echo "📥 Downloading upgraded model (llava:13b-v1.6)..."
echo "   This may take 5-10 minutes (7-8 GB download)"
echo ""
ollama pull llava:13b-v1.6
echo ""

# Verify installation
echo "✅ Verifying installation..."
echo ""

echo "Testing image processor..."
python3 -c "
from advanced_image_processor import AdvancedImageProcessor
from PIL import Image
import numpy as np

processor = AdvancedImageProcessor(enhance_mode='balanced')
test_img = Image.new('RGB', (1920, 1080), color='blue')
processed = processor.preprocess_for_vision_model(test_img)
print('   ✅ Image processor working')
print(f'   ✅ Processed size: {processed.size}')
" 2>&1

echo ""

# Check models available
echo "📋 Available Ollama models:"
ollama list
echo ""

# All done
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE!                                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎮 To start the enhanced commentary system:"
echo ""
echo "   python3 gameplay_commentator_enhanced.py"
echo ""
echo "📚 Read the guides:"
echo "   • ENHANCEMENT_SUMMARY.md - Complete overview"
echo "   • QUICK_REFERENCE.md - Quick commands"
echo "   • MODEL_IMPROVEMENT_GUIDE.md - Optimization tips"
echo "   • CUSTOM_MODEL_TRAINING_ROADMAP.md - Train your own AI"
echo ""
echo "🎯 Next steps:"
echo "   1. Run: python3 gameplay_commentator_enhanced.py"
echo "   2. Play a game and test it!"
echo "   3. Read ENHANCEMENT_SUMMARY.md for details"
echo ""
echo "Happy gaming! 🎮🎙️"
