# Infrastructure Tests

Tests for Docker Compose environment setup and infrastructure components.

## Testing Philosophy

**CRITICAL**: All infrastructure tests run against the **production environment** - **NEVER with placeholders**.

- Tests connect to **real Docker containers** from `docker-compose.yml`
- Tests validate **actual service health** (PostgreSQL, Kafka, Zookeeper, Airflow)
- Tests check **real network connectivity** between services
- Tests verify **actual volume persistence** in production volumes
- Tests use **real service endpoints** (not mocked)

**No placeholders. No mocks. Production Docker Compose environment only.**

## Test Files

### `test_docker_compose.py`
Docker Compose configuration and setup validation tests.

**Test Classes**:
- `TestDockerComposeConfig`: Configuration file validation
- `TestDirectoryStructure`: Required directory checks
- `TestDockerInstallation`: Docker/Docker Compose installation

**Markers**: `@pytest.mark.docker`

### `test_services.py`
Service health and functionality tests.

**Test Classes**:
- `TestServiceStartup`: Service startup verification
- `TestServiceHealth`: Health check validation
- `TestServiceLogs`: Log error detection

**Markers**: `@pytest.mark.docker`, `@pytest.mark.integration`, `@pytest.mark.health`, `@pytest.mark.slow`

### `test_networking.py`
Network connectivity and service communication tests.

**Test Classes**:
- `TestPortAccessibility`: Port accessibility checks
- `TestServiceCommunication`: Service-to-service communication
- `TestKafkaConnectivity`: Kafka-specific connectivity

**Markers**: `@pytest.mark.docker`, `@pytest.mark.integration`, `@pytest.mark.network`

### `test_volumes.py`
Volume persistence and data storage tests.

**Test Classes**:
- `TestVolumePersistence`: Data persistence across restarts

**Markers**: `@pytest.mark.docker`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.volume`

## Running Tests

```bash
# Run all infrastructure tests
pytest project/tests/infrastructure/

# Run specific test file
pytest project/tests/infrastructure/test_docker_compose.py

# Run with markers
pytest project/tests/infrastructure/ -m health
pytest project/tests/infrastructure/ -m network
```

## Dependencies

See `requirements-test.txt` for test dependencies.

