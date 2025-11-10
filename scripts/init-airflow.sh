#!/bin/bash
# init-airflow.sh
# Airflow Database Initialization and Admin User Creation Script
#
# This script initializes the Airflow database and creates an admin user.
# It uses docker-compose run --rm to create one-off containers for execution,
# which allows initialization even if the webserver service isn't running yet.
#
# Usage:
#   ./scripts/init-airflow.sh
#
# Prerequisites:
#   - Docker Compose services must be running (at minimum: postgres)
#   - PostgreSQL service must be healthy
#   - FERNET_KEY must be set in .env file
#
# Implementation Notes:
#   - Uses 'airflow db init' (deprecated but functional)
#   - Uses 'docker-compose run --rm' for one-off container execution
#   - Handles duplicate user detection gracefully
#   - Includes comprehensive error handling and retry logic

set -e  # Exit on error

echo "=========================================="
echo "Airflow Initialization Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose command not found. Please install Docker Compose."
    exit 1
fi

# Check if services are running
print_status "Checking if Docker Compose services are running..."
if ! docker-compose ps | grep -q "Up"; then
    print_warning "Docker Compose services may not be running. Starting services..."
    docker-compose up -d postgres
    sleep 5
fi

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

until docker-compose exec -T postgres pg_isready -U airflow > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        print_error "PostgreSQL failed to become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""
print_status "PostgreSQL is ready!"

# Initialize Airflow database
# Use docker-compose run to create a one-off container for initialization
# This works even if the webserver service isn't running yet
print_status "Initializing Airflow database..."
if docker-compose run --rm airflow-webserver airflow db init 2>&1 | tee /tmp/airflow_init.log; then
    print_status "Airflow database initialized successfully!"
else
    # Check if database was already initialized
    if grep -q "already initialized\|already exists\|Database already initialized\|Initialization done" /tmp/airflow_init.log 2>/dev/null; then
        print_warning "Airflow database appears to be already initialized. Skipping database init."
    else
        print_error "Failed to initialize Airflow database"
        cat /tmp/airflow_init.log
        exit 1
    fi
fi

# Check if admin user already exists
# Use docker-compose run for one-off container execution
print_status "Checking if admin user exists..."
if docker-compose run --rm airflow-webserver airflow users list 2>/dev/null | grep -q "admin"; then
    print_warning "Admin user already exists. Skipping user creation."
    print_status "Existing admin users:"
    docker-compose run --rm airflow-webserver airflow users list
else
    # Create admin user
    print_status "Creating admin user..."
    if docker-compose run --rm airflow-webserver airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin 2>&1; then
        print_status "Admin user created successfully!"
        print_warning "Default credentials: username=admin, password=admin"
        print_warning "Please change the password in production!"
    else
        print_error "Failed to create admin user"
        exit 1
    fi
fi

# Verify Airflow configuration
print_status "Verifying Airflow configuration..."
docker-compose run --rm airflow-webserver airflow config list | grep -E "(executor|database|fernet)" || true

# Test Airflow CLI commands
print_status "Testing Airflow CLI commands..."
if docker-compose run --rm airflow-webserver airflow version > /dev/null 2>&1; then
    print_status "Airflow CLI is working correctly"
    docker-compose run --rm airflow-webserver airflow version
else
    print_error "Airflow CLI test failed"
    exit 1
fi

# List DAGs (should be empty initially)
print_status "Checking DAGs folder..."
if docker-compose run --rm airflow-webserver airflow dags list 2>&1 | head -5; then
    print_status "DAGs command executed successfully"
else
    print_warning "DAGs list command had issues (this may be normal if no DAGs exist)"
fi

echo ""
echo "=========================================="
print_status "Airflow initialization complete!"
echo "=========================================="
echo ""
print_status "Next steps:"
echo "  1. Access Airflow UI at: http://localhost:8080"
echo "  2. Login with: admin / admin"
echo "  3. Start creating DAGs in project/dags/"
echo ""
print_warning "Remember to change the admin password in production!"
echo ""

