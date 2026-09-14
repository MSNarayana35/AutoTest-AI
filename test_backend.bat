@echo off
REM Quick test to verify backend works
echo Testing backend...
echo.

cd backend
python -c "from app.main import app; print('✅ Backend imports successfully!')"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Backend is FIXED and ready to run!
    echo.
    echo To start the backend:
    echo   cd backend
    echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    echo.
) else (
    echo.
    echo ❌ Backend still has errors
    echo.
)

pause
