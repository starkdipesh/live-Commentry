#!/bin/bash
# Saarthika Complete Setup Script for Fresh Linux Installation
# This will set up everything needed to run Saarthika on a new laptop

set -e  # Exit on any error

echo "======================================================================"
echo "  🕉️ SAARTHIKA - Complete Installation Setup"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}  ✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}  ⚠️ ${NC} $1"
}

print_error() {
    echo -e "${RED}  ❌${NC} $1"
}

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    print_error "This script is for Linux only!"
    exit 1
fi

print_success "Linux detected: $(lsb_release -d | cut -f2)"

# Step 1: Check Python 3
print_step "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    echo "  Install it with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Found: $PYTHON_VERSION"

# Step 2: Check if venv exists
print_step "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv venv
    print_success "Created venv"
else
    print_success "Virtual environment already exists"
fi

# Step 3: Activate venv and upgrade pip
print_step "Activating venv and upgrading pip..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel
print_success "Pip upgraded"

# Step 4: Install Python dependencies
print_step "Installing Python dependencies..."
pip install -r requirements.txt
print_success "All Python packages installed"

# Step 5: Install system dependencies (optional but recommended)
print_step "Checking system dependencies..."

# Check for basic tools
if ! command -v curl &> /dev/null; then
    print_warning "curl not found. Install with: sudo apt install curl"
fi

# Critical: Install Audio & Screenshot Tools
print_step "Installing system audio & screenshot dependencies..."
# We try to install them automatically
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y portaudio19-dev python3-pyaudio gnome-screenshot
    print_success "System dependencies installed"
else
    print_warning "Not Ubuntu/Debian? Please manually install: portaudio19-dev, gnome-screenshot"
fi

# Step 6: Setup .env file
print_step "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env file created from template"
        echo "  ⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY"
        echo "  Get your key from: https://console.groq.com/keys"
    else
        cat > .env << EOL
# Saarthika Environment Configuration
GROQ_API_KEY=your_api_key_here
EOL
        print_warning ".env file created"
        echo "  ⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY"
    fi
else
    # Check if API key is set
    if grep -q "your_api_key_here" .env || grep -q "^GROQ_API_KEY=$" .env; then
        print_warning ".env exists but API key not set"
        echo "  ⚠️  Edit .env and add your GROQ_API_KEY"
    else
        print_success ".env configured"
    fi
fi

# Step 7: Create necessary directories
print_step "Creating data directories..."
mkdir -p training_data/gold_dataset
mkdir -p config
print_success "Directories created"

# Step 8: Test internet connectivity
print_step "Testing internet connection..."
if curl -s --head --request GET https://api.groq.com | grep "200" > /dev/null; then
    print_success "Internet connection OK - Groq API reachable"
else
    print_warning "Cannot reach Groq API - check internet connection"
fi

# Step 9: Check desktop environment
print_step "Checking desktop environment..."
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    print_warning "Wayland detected"
    echo "  Use Xorg for best screen capture performance."
    echo "  However, Saarthika will try to run anyway."
else
    print_success "Xorg detected - Perfect for Screen Capture"
fi

# Step 10: Run diagnostic
print_step "Running system diagnostic..."
./venv/bin/python3 diagnose.py

echo ""
echo "======================================================================"
echo "  ✨ INSTALLATION COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API key:"
echo "   nano .env"
echo "   (Add your GROQ_API_KEY)"
echo ""
echo "2. Start Saarthika:"
echo "   ./venv/bin/python3 main.py"
echo ""
echo "======================================================================"
echo "  📚 Documentation:"
echo "  - LAPTOP_SETUP_GUIDE.md"
echo "  - SYSTEM_OVERVIEW.md"
echo "======================================================================"
echo ""
echo "🕉️ Boss, your Strategic Shadow is ready! 🕉️👑🤴🛡️✨"
echo ""
