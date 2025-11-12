#!/bin/bash
# Test script for Docker Compose environment setup
# Usage: ./project/scripts/test-docker-compose.sh

set -e  # Exit on error

echo "=========================================="
echo "Docker Compose Environment Testing"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Docker Compose syntax validation
echo "Test 1: Validating Docker Compose file syntax..."
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose file syntax is valid"
else
    echo -e "${RED}✗${NC} Docker Compose file has syntax errors"
    docker-compose config
    exit 1
fi
echo ""

# Test 2: Check if .env file exists
echo "Test 2: Checking for .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    if grep -q "FERNET_KEY=" .env && ! grep -q "your_fernet_key_here" .env; then
        echo -e "${GREEN}✓${NC} FERNET_KEY is set in .env"
    else
        echo -e "${YELLOW}⚠${NC} FERNET_KEY not properly configured in .env"
        echo "   Run: ./project/scripts/generate-fernet-key.sh"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "   Create .env file from .env.example"
    echo "   Run: cp .env.example .env"
    echo "   Then generate FERNET_KEY: ./project/scripts/generate-fernet-key.sh"
fi
echo ""

# Test 3: Check required directories
echo "Test 3: Checking required directories..."
REQUIRED_DIRS=("project/dags" "project/logs" "project/plugins")
ALL_DIRS_EXIST=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} Directory exists: $dir"
    else
        echo -e "${RED}✗${NC} Directory missing: $dir"
        ALL_DIRS_EXIST=false
    fi
done

if [ "$ALL_DIRS_EXIST" = false ]; then
    echo "Creating missing directories..."
    mkdir -p "${REQUIRED_DIRS[@]}"
fi
echo ""

# Test 4: Check Docker and Docker Compose availability
echo "Test 4: Checking Docker and Docker Compose..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not installed"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose installed: $COMPOSE_VERSION"
else
    echo -e "${RED}✗${NC} Docker Compose not installed"
    exit 1
fi
echo ""

# Test 5: Check if ports are available
echo "Test 5: Checking port availability..."
PORTS=(8080 9092 2181)
PORT_CONFLICTS=false
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $port is already in use"
        PORT_CONFLICTS=true
    else
        echo -e "${GREEN}✓${NC} Port $port is available"
    fi
done

if [ "$PORT_CONFLICTS" = true ]; then
    echo "   Warning: Some ports are in use. Services may fail to start."
fi
echo ""

# Test 6: Validate service definitions
echo "Test 6: Validating service definitions..."
REQUIRED_SERVICES=("postgres" "zookeeper" "kafka" "airflow-webserver" "airflow-scheduler")
for service in "${REQUIRED_SERVICES[@]}"; do
    if docker-compose config | grep -q "^  $service:"; then
        echo -e "${GREEN}✓${NC} Service defined: $service"
    else
        echo -e "${RED}✗${NC} Service missing: $service"
    fi
done
echo ""

# Summary
echo "=========================================="
echo "Testing Summary"
echo "=========================================="
echo ""
echo "Pre-flight checks completed."
echo ""
echo "Next steps:"
echo "1. Ensure .env file exists with FERNET_KEY"
echo "2. Start services: docker-compose up -d"
echo "3. Check service health: docker-compose ps"
echo "4. Access Airflow UI: http://localhost:8080"
echo "5. Verify Kafka: docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092"
echo ""

