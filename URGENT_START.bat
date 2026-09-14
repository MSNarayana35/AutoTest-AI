@echo off
echo ================================================
echo   AUTOTEST AI - URGENT START
echo ================================================
echo.

REM Start backend
echo Starting Backend...
start "AutoTest AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting Frontend...
start "AutoTest AI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo   ✅ APP STARTING!
echo ================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Both servers running in separate windows!
echo.
pause
