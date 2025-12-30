#!/bin/bash

# PARTHASARATHI SETUP SCRIPT
# This script prepares a fresh Linux machine for the AI Gaming Partner.

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   PARTHASARATHI AI - SYSTEM INSTALLER (v1.0)   ${NC}"
echo -e "${BLUE}==================================================${NC}"

# 1. System Dependencies
echo -e "\n${GREEN}[1/5] Installing System Dependencies...${NC}"
sudo apt update
sudo apt install -y python3-venv python3-pip python3-pyaudio libportaudio2 libatlas-base-dev libx11-dev libxtst-dev libpng-dev mpg123
if [ $? -eq 0 ]; then
    echo -e "✅ System dependencies installed."
else
    echo -e "${RED}❌ Failed to install system dependencies.${NC}"
    exit 1
fi

# 2. Ollama Installation & Model Pulling
echo -e "\n${GREEN}[2/5] Checking AI Brain (Ollama)...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "⚙️ Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo -e "✅ Ollama is already installed."
fi

# Ensure Ollama service is running
if ! systemctl is-active --quiet ollama; then
    echo -e "⚙️ Starting Ollama service..."
    sudo systemctl start ollama
fi

echo -e "🧠 Downloading AI Models (This may take time via internet)..."
echo -e "   - Pulling Vision Brain (llava-phi3)..."
ollama pull llava-phi3
echo -e "   - Pulling Logic Brain (phi3:mini)..."
ollama pull phi3:mini

echo -e "🧠 Creating Custom Mind (Parthasarathi-Mind)..."
ollama create Parthasarathi-Mind -f Modelfile

# 3. Python Environment
echo -e "\n${GREEN}[3/5] Setting up Python Environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "✅ Virtual Environment created."
else
    echo -e "✅ Virtual Environment already exists."
fi

# Activate and Install
source venv/bin/activate
echo -e "📦 Installing Python Libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Directory Structure
echo -e "\n${GREEN}[4/5] initializing Data Directories...${NC}"
mkdir -p training_data/gold_dataset
mkdir -p training_data/raw_captures
mkdir -p config
mkdir -p src/core/tmp
echo -e "✅ Directories created."

# 5. Permission Fixes
chmod +x run.py

echo -e "\n${BLUE}==================================================${NC}"
echo -e "${GREEN}   ✨ INSTALLATION COMPLETE! ✨   ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "To start Parthasarathi:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "   ${GREEN}python3 run.py interactive${NC}"
echo -e ""
