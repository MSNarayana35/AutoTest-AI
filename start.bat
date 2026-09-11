@echo off
REM ============================================================
REM AutoTest AI - Quick Start Script for Windows
REM ============================================================

echo ================================================
echo    AutoTest AI - Starting...
echo ================================================
echo.

REM ------------------------------------------------------------
REM Step 1: Check Python installation
REM ------------------------------------------------------------
echo [1/6] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Download Python 3.10+
    echo   3. IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    echo After installing, close this terminal and run start.bat again!
    echo.
    pause
    exit /b 1
)
echo ✅ Python found!
python --version
echo.

REM ------------------------------------------------------------
REM Step 2: Check Node.js installation
REM ------------------------------------------------------------
echo [2/6] Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found!
    echo.
    echo Please install Node.js:
    echo   1. Go to https://nodejs.org/
    echo   2. Download the LTS (Long Term Support) version
    echo   3. Run the installer (check all boxes)
    echo.
    echo After installing, close this terminal and run start.bat again!
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js found!
node --version
npm --version
echo.

REM ------------------------------------------------------------
REM Step 3: Setup Backend
REM ------------------------------------------------------------
echo [3/6] Setting up Backend...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment!
        pause
        exit /b 1
    )
)

if not exist "uploads" (
    mkdir uploads
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
echo ✅ Backend dependencies ready!
cd ..
echo.

REM ------------------------------------------------------------
REM Step 4: Setup Frontend
REM ------------------------------------------------------------
echo [4/6] Setting up Frontend...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install frontend dependencies!
        pause
        exit /b 1
    )
)
echo ✅ Frontend dependencies ready!
cd ..
echo.

REM ------------------------------------------------------------
REM Step 5: Start Servers
REM ------------------------------------------------------------
echo [5/6] Starting Backend Server...
start "AutoTest AI - Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo [6/6] Starting Frontend Server...
start "AutoTest AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo    🚀 AutoTest AI is Starting!
echo ================================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3000
echo.
echo Both servers are running in separate windows!
echo.
echo Press any key to close this window (servers keep running)
pause >nul
