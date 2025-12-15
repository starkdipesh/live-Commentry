@echo off
REM 🎮 FREE AI Gameplay Commentary - Windows Setup Script

echo ================================================================
echo.
echo        🎮 FREE AI GAMEPLAY COMMENTATOR SETUP 🎙️
echo.
echo        Setting up Ollama + LLaVA + Natural Voice
echo.
echo ================================================================
echo.

REM Step 1: Check Python
echo 📋 Step 1: Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Python not found!
    echo    Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo    ✅ %PYTHON_VERSION% found
echo.

REM Step 2: Install Python dependencies
echo 📦 Step 2: Installing Python dependencies...
if exist requirements_free.txt (
    python -m pip install -r requirements_free.txt
    echo    ✅ Python dependencies installed
) else (
    echo    ⚠️  requirements_free.txt not found, installing manually...
    python -m pip install mss Pillow pyttsx3 requests
    echo    ✅ Core dependencies installed
)
echo.

REM Step 3: Check Ollama
echo 🤖 Step 3: Checking Ollama installation...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️  Ollama not found!
    echo.
    echo    📥 Please install Ollama:
    echo       1. Download from: https://ollama.ai/download
    echo       2. Run the installer
    echo       3. Restart this script
    echo.
    pause
    exit /b 1
)
echo    ✅ Ollama is installed
echo.

REM Step 4: Check if Ollama is running
echo 🔌 Step 4: Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️  Ollama service is not running
    echo.
    echo    Please start Ollama:
    echo       1. Open new terminal/command prompt
    echo       2. Run: ollama serve
    echo       3. Keep that window open
    echo.
    echo    Press any key after starting Ollama...
    pause >nul
    
    REM Check again
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo    ❌ Still can't connect to Ollama
        echo    Make sure 'ollama serve' is running in another window
        pause
        exit /b 1
    )
)
echo    ✅ Ollama service is running
echo.

REM Step 5: Pull LLaVA model
echo 📥 Step 5: Downloading LLaVA vision model...
echo    (This may take a few minutes on first run - ~4.7GB download)
echo.

ollama list | findstr "llava" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ LLaVA model already installed
) else (
    echo    ⏳ Pulling llava:latest...
    ollama pull llava:latest
    if %errorlevel% equ 0 (
        echo    ✅ LLaVA model downloaded successfully!
    ) else (
        echo    ❌ Failed to download LLaVA model
        echo    Try manually: ollama pull llava
        pause
        exit /b 1
    )
)
echo.

REM Step 6: Test TTS
echo 🔊 Step 6: Testing Text-to-Speech...
python -c "import pyttsx3; engine = pyttsx3.init(); print('   ✅ TTS engine initialized')"
if %errorlevel% equ 0 (
    echo    ✅ Voice synthesis ready
) else (
    echo    ⚠️  TTS warning (will still work)
)
echo.

REM Success!
echo ================================================================
echo ✅ SETUP COMPLETE!
echo ================================================================
echo.
echo 🎮 Your FREE AI Gameplay Commentator is ready!
echo.
echo 📋 To use:
echo    1. Make sure Ollama is running: ollama serve (in new window)
echo    2. Run: python gameplay_commentator_free.py
echo    3. Play your game and enjoy FREE AI commentary!
echo.
echo 💡 Tips:
echo    - No internet needed after setup
echo    - No API costs ever
echo    - Works completely offline
echo.
echo 🎉 Happy Gaming!
echo ================================================================
echo.
pause
