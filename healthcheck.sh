#!/bin/bash

# AutoTest AI - Health Check Script
# Checks the health of all services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================"
echo "   AutoTest AI - Health Check"
echo "================================================"
echo ""

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $service_name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (HTTP $response)"
        return 1
    fi
}

# Check Docker
echo -e "${BLUE}=== Docker Status ===${NC}"
if docker ps &> /dev/null; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi
echo ""

# Check Containers
echo -e "${BLUE}=== Container Status ===${NC}"
docker-compose -f docker-compose.prod.yml ps
echo ""

# Check Services
echo -e "${BLUE}=== Service Health Checks ===${NC}"

# Backend Health
check_service "Backend API" "http://localhost:8000/health" || true

# Backend Docs
check_service "API Documentation" "http://localhost:8000/docs" || true

# Frontend
check_service "Frontend" "http://localhost:3000" || true

# Nginx
check_service "Nginx" "http://localhost" || true

echo ""

# Check Database
echo -e "${BLUE}=== Database Status ===${NC}"
if docker exec autotest_postgres_prod pg_isready -U postgres &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
    
    # Check connection
    if docker exec autotest_postgres_prod psql -U postgres -d autotest_prod -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
        
        # Count tables
        table_count=$(docker exec autotest_postgres_prod psql -U postgres -d autotest_prod -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | xargs)
        echo -e "${GREEN}✅ Database tables: $table_count${NC}"
    else
        echo -e "${RED}❌ Database connection failed${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
fi
echo ""

# Check Disk Space
echo -e "${BLUE}=== System Resources ===${NC}"
df -h | grep -E '^Filesystem|/$'
echo ""

# Check Docker Resources
echo -e "${BLUE}=== Docker Resource Usage ===${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

# Check Logs for Errors
echo -e "${BLUE}=== Recent Errors (Last 10) ===${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i "error" | tail -10 || echo "No recent errors found"
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}Health Check Complete${NC}"
echo "================================================"
echo ""
echo "For detailed logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To restart a service:"
echo "  docker-compose -f docker-compose.prod.yml restart <service>"
echo ""
