@echo off
REM AutoTest AI - Production Deployment Script for Windows
REM This script deploys the application in production mode with Docker Compose

echo ================================================
echo    AutoTest AI - Production Deployment
echo ================================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [IMPORTANT] Edit .env file with your production credentials!
    echo Press any key to continue after editing .env...
    pause > nul
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist backend\uploads mkdir backend\uploads
if not exist backend\logs mkdir backend\logs
if not exist nginx\logs mkdir nginx\logs
if not exist nginx\ssl mkdir nginx\ssl
if not exist backups mkdir backups

REM Build and start services
echo.
echo Building Docker images...
docker-compose -f docker-compose.prod.yml build --no-cache

echo.
echo Starting services...
docker-compose -f docker-compose.prod.yml up -d

REM Wait for services
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak > nul

REM Check service status
echo.
echo Checking service status...
docker-compose -f docker-compose.prod.yml ps

REM Check backend health
echo.
echo Checking backend health...
timeout /t 5 /nobreak > nul
curl -f http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend might still be starting...
) else (
    echo [OK] Backend is healthy!
)

REM Check frontend
echo.
echo Checking frontend...
curl -f http://localhost:3000 > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Frontend might still be starting...
) else (
    echo [OK] Frontend is responding!
)

echo.
echo ================================================
echo [SUCCESS] Deployment Complete!
echo ================================================
echo.
echo Access your application:
echo    Frontend: http://localhost
echo    Backend API: http://localhost/api
echo    API Docs: http://localhost/docs
echo.
echo View logs:
echo    docker-compose -f docker-compose.prod.yml logs -f
echo.
echo Stop services:
echo    docker-compose -f docker-compose.prod.yml down
echo.
echo Restart services:
echo    docker-compose -f docker-compose.prod.yml restart
echo.
pause
