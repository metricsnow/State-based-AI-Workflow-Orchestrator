# Testing Guide: Phase 1 - Docker Compose Environment

## Overview

This guide provides comprehensive testing procedures for the Docker Compose environment setup (TASK-001).

**Status**: ✅ Testing suite implemented with modular structure

## Test Suite Structure

The test suite is organized by module in `project/tests/`:

```
project/tests/
├── infrastructure/          # Docker Compose & infrastructure tests
│   ├── test_docker_compose.py   # Configuration tests (11 tests)
│   ├── test_services.py         # Service health tests
│   ├── test_networking.py       # Network connectivity tests
│   └── test_volumes.py          # Volume persistence tests
├── airflow/                # Airflow tests (Phase 1.2+)
└── kafka/                  # Kafka tests (Phase 1.3+)
```

See `project/tests/README.md` for detailed test suite documentation.

## Pre-Flight Testing

### Automated Pre-Flight Checks

**Option 1: Pytest Test Suite** (Recommended)
```bash
source venv/bin/activate
pip install -r project/tests/infrastructure/requirements-test.txt
pytest project/tests/infrastructure/test_docker_compose.py -v
```

**Option 2: Shell Script**
```bash
./scripts/test-docker-compose.sh
```

Both methods validate:
- Docker Compose file syntax
- .env file existence and FERNET_KEY configuration
- Required directory structure
- Docker and Docker Compose installation
- Port availability
- Service definitions

**Test Results**: ✅ 11/11 configuration tests passing

### Manual Pre-Flight Checks

1. **Verify Docker is running**:
   ```bash
   docker ps
   ```

2. **Check Docker Compose version**:
   ```bash
   docker-compose --version
   ```

3. **Verify .env file exists**:
   ```bash
   ls -la .env
   ```

4. **Generate FERNET_KEY if needed**:
   ```bash
   source venv/bin/activate
   ./scripts/generate-fernet-key.sh
   ```

## Service Startup Testing

### Start All Services

```bash
docker-compose up -d
```

### Verify Service Status

```bash
docker-compose ps
```

Expected output should show all services as "healthy" or "running":
- `airflow-postgres`: healthy
- `airflow-zookeeper`: healthy
- `airflow-kafka`: healthy
- `airflow-webserver`: healthy
- `airflow-scheduler`: running

### Check Service Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
docker-compose logs kafka
```

## Service Health Validation

### PostgreSQL Health Check

```bash
docker-compose exec postgres pg_isready -U airflow
```

Expected: `postgres:5432 - accepting connections`

### Zookeeper Health Check

```bash
docker-compose exec zookeeper nc -z localhost 2181
```

Expected: Exit code 0 (success)

### Kafka Health Check

```bash
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

Expected: List of API versions (no errors)

### Airflow Webserver Health Check

```bash
curl http://localhost:8080/health
```

Expected: HTTP 200 response

Or access in browser: http://localhost:8080

### Airflow Scheduler Check

```bash
docker-compose logs airflow-scheduler | tail -20
```

Expected: No critical errors, scheduler running

## Network Connectivity Testing

### Test Service-to-Service Communication

```bash
# Test Airflow to PostgreSQL
docker-compose exec airflow-webserver ping -c 2 postgres

# Test Kafka to Zookeeper
docker-compose exec kafka ping -c 2 zookeeper
```

### Test External Access

```bash
# Test Airflow UI
curl -I http://localhost:8080

# Test Kafka (requires kafka-python or kafkacat)
# Install: pip install kafka-python
python3 -c "from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers=['localhost:9092']); print('Kafka accessible')"
```

## Volume Persistence Testing

### Test PostgreSQL Volume

```bash
# Create test data
docker-compose exec postgres psql -U airflow -d airflow -c "CREATE TABLE test_table (id INT);"

# Stop services
docker-compose down

# Start services again
docker-compose up -d

# Wait for services to be healthy
sleep 30

# Verify data persists
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT * FROM test_table;"
```

Expected: Table and data should still exist

## Service Restart Testing

### Test Individual Service Restart

```bash
# Restart a service
docker-compose restart airflow-webserver

# Verify it recovers
docker-compose ps airflow-webserver
```

### Test Full Stack Restart

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Verify all services recover
docker-compose ps
```

## Integration Testing

### Test Airflow Database Connection

```bash
docker-compose exec airflow-webserver airflow db check
```

Expected: Database connection successful

### Test Kafka Topic Creation

```bash
docker-compose exec kafka kafka-topics --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# List topics
docker-compose exec kafka kafka-topics --list \
  --bootstrap-server localhost:9092
```

Expected: `test-topic` appears in list

## Performance Testing

### Check Resource Usage

```bash
docker stats --no-stream
```

Monitor:
- CPU usage per container
- Memory usage per container
- Network I/O

### Check Service Startup Time

```bash
time docker-compose up -d
```

Expected: All services start within 2-3 minutes

## Troubleshooting Tests

### Test Service Dependencies

```bash
# Stop PostgreSQL and verify Airflow fails gracefully
docker-compose stop postgres
docker-compose logs airflow-webserver | tail -10

# Restart PostgreSQL
docker-compose start postgres
```

### Test Health Check Failures

```bash
# Manually fail a health check
docker-compose exec postgres pg_ctl stop

# Verify dependent services handle failure
docker-compose ps
```

## Cleanup Testing

### Test Clean Shutdown

```bash
docker-compose down
```

Verify:
- All containers stopped
- Network removed
- Volumes preserved (for postgres_data)

### Test Complete Cleanup

```bash
docker-compose down -v
```

**Warning**: This removes all volumes including database data!

## Acceptance Criteria Validation

Use this checklist to validate TASK-001 completion:

- [ ] Docker Compose file syntax valid
- [ ] All services start successfully
- [ ] All health checks passing
- [ ] Airflow webserver accessible at http://localhost:8080
- [ ] Airflow scheduler running
- [ ] Kafka accessible on port 9092
- [ ] PostgreSQL database initialized
- [ ] Services can communicate via Docker network
- [ ] Volume persistence working
- [ ] Service restart works correctly
- [ ] .env.example file created
- [ ] Documentation complete

## Running Tests with Pytest

### Configuration Tests (Fast, No Services Required)
```bash
pytest project/tests/infrastructure/test_docker_compose.py -v
```

**Expected**: 11 tests passing

### Integration Tests (Requires Running Services)
```bash
# Start services first
docker-compose up -d

# Run integration tests
pytest project/tests/infrastructure/test_services.py -v
pytest project/tests/infrastructure/test_networking.py -v
pytest project/tests/infrastructure/test_volumes.py -v
```

### Run All Infrastructure Tests
```bash
pytest project/tests/infrastructure/ -v
```

### Run with Markers
```bash
pytest project/tests/infrastructure/ -m health    # Health check tests
pytest project/tests/infrastructure/ -m network  # Network tests
pytest project/tests/infrastructure/ -m volume    # Volume tests
pytest project/tests/infrastructure/ -m integration  # All integration tests
```

## Test Results Template

```markdown
## Test Results - [Date]

### Pre-Flight Checks (pytest)
- [x] Docker Compose syntax: PASS (11/11 tests)
- [x] .env file: PASS
- [x] Directories: PASS
- [x] Docker installed: PASS
- [x] Ports available: PASS

### Service Startup
- [ ] All services started: PASS/FAIL
- [ ] Health checks passing: PASS/FAIL
- [ ] No errors in logs: PASS/FAIL

### Integration
- [ ] Airflow UI accessible: PASS/FAIL
- [ ] Kafka accessible: PASS/FAIL
- [ ] Database connection: PASS/FAIL

### Persistence
- [ ] Volume persistence: PASS/FAIL
- [ ] Service restart: PASS/FAIL

### Notes
[Any issues or observations]
```

## Test Suite Documentation

For detailed test suite documentation, see:
- **Main Test Suite**: `project/tests/README.md`
- **Infrastructure Tests**: `project/tests/infrastructure/README.md`
- **Pytest Configuration**: `pytest.ini`

## Next Steps

After successful testing:
1. ✅ TASK-001: Docker Compose Environment Setup - **COMPLETE**
2. Proceed to TASK-002: Airflow Configuration and Initialization
3. Document any issues encountered
4. Run integration tests when services are started

