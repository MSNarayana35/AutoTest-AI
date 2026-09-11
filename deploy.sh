#!/bin/bash

# AutoTest AI - Production Deployment Script
# This script deploys the application in production mode with Docker Compose

set -e  # Exit on error

echo "================================================"
echo "   AutoTest AI - Production Deployment"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ IMPORTANT: Edit .env file with your production credentials!${NC}"
    echo "   Press Enter to continue after editing .env..."
    read
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads backend/logs nginx/logs nginx/ssl backups

# Pull latest changes (if using Git)
if [ -d .git ]; then
    echo "🔄 Pulling latest changes from Git..."
    git pull origin main || echo "⚠️  Git pull failed or not using Git"
fi

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Check backend health
echo ""
echo "🏥 Checking backend health..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi
    echo "⏳ Waiting for backend... ($i/10)"
    sleep 3
done

# Check frontend
echo ""
echo "🌐 Checking frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend might still be starting...${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo "   API Docs: http://localhost/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🔄 Restart services:"
echo "   docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "🗄️  Backup database:"
echo "   docker exec autotest_postgres_prod pg_dump -U postgres autotest_prod > backups/backup_\$(date +%Y%m%d_%H%M%S).sql"
echo ""
