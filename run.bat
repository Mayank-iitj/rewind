@echo off
REM Quick Start Script for LoL Analytics Agent (Windows)

echo ========================================
echo League of Legends Analytics Agent
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file from .env.example:
    echo   copy .env.example .env
    echo.
    echo Then edit .env with your API keys.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check for Riot API key
findstr /C:"RIOT_API_KEY=RGAPI" .env >nul
if %errorlevel%==0 (
    echo.
    echo [WARNING] Please update RIOT_API_KEY in .env file
    echo Get your key from: https://developer.riotgames.com/
    echo.
)

REM Run the application
echo.
echo ========================================
echo Starting LoL Analytics Agent...
echo ========================================
echo.
echo Access the app at: http://localhost:5000
echo.
python app.py

pause
