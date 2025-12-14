@echo off
REM Windows Quick Fix Script for AI Commentary System
REM This creates the tmp folder and tests permissions

echo.
echo ========================================
echo   Windows Quick Fix Tool
echo ========================================
echo.

REM Create tmp folder
echo Creating tmp folder...
if not exist "tmp" (
    mkdir tmp
    echo [OK] tmp folder created
) else (
    echo [OK] tmp folder already exists
)

REM Test write permission
echo.
echo Testing write permissions...
echo test > tmp\test.txt 2>nul
if exist "tmp\test.txt" (
    del tmp\test.txt
    echo [OK] Write permissions working!
) else (
    echo [ERROR] Cannot write to tmp folder!
    echo Please run this script as Administrator:
    echo 1. Right-click on fix_windows.bat
    echo 2. Select "Run as administrator"
    goto :error
)

REM Check Python
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    goto :error
) else (
    echo [OK] Python is installed
)

REM Check dependencies
echo.
echo Checking dependencies...
python -c "import gtts; import pygame; print('[OK] All dependencies installed')" 2>nul
if errorlevel 1 (
    echo [WARNING] Some dependencies missing
    echo Installing now...
    pip install gtts pygame Pillow mss python-dotenv
)

REM Run diagnostic
echo.
echo Running diagnostic test...
python test_windows_permissions.py

REM Success
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo You can now run the commentary system:
echo   python gameplay_commentator.py
echo.
pause
goto :end

:error
echo.
echo ========================================
echo   Setup Failed!
echo ========================================
echo.
echo Please check the errors above and:
echo 1. Run as Administrator
echo 2. Check antivirus settings
echo 3. See WINDOWS_FIX.md for help
echo.
pause
exit /b 1

:end
exit /b 0
