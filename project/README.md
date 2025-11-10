# Project Root

This directory contains the main project implementation for Phase 1.

## Directory Structure

- `dags/` - Airflow DAG definitions
- `logs/` - Airflow execution logs
- `plugins/` - Airflow custom plugins
- `dev/` - Development artifacts (tasks, bugs)
- `docs/` - Project documentation (PRDs)
- `tests/` - Test suite organized by module
  - `infrastructure/` - Docker Compose and infrastructure tests
  - `airflow/` - Airflow DAG and workflow tests (Phase 1.2+)
  - `kafka/` - Kafka producer/consumer tests (Phase 1.3+)

## Quick Start

1. Ensure Docker and Docker Compose are installed
2. Generate FERNET_KEY: `./scripts/generate-fernet-key.sh`
3. Copy `.env.example` to `.env` and update FERNET_KEY (or use existing `.env` if already created)
4. Verify configuration: `pytest project/tests/infrastructure/test_docker_compose.py -v`
5. Start services: `docker-compose up -d`
6. **Note**: Airflow UI requires TASK-002 (database initialization) before it can be accessed

## Services

- **Airflow Webserver**: http://localhost:8080 (requires TASK-002: database initialization)
- **Kafka**: localhost:9092 ✅ Verified
- **PostgreSQL**: Internal (port 5432) ✅ Verified

**Status**: Infrastructure services (PostgreSQL, Zookeeper, Kafka) are operational. Airflow services require database initialization (TASK-002).

## Testing

### Running Tests

**Infrastructure tests** (Docker Compose, services):
```bash
source venv/bin/activate
pip install -r project/tests/infrastructure/requirements-test.txt
pytest project/tests/infrastructure/ -v
```

**All tests**:
```bash
pytest project/tests/ -v
```

**By marker**:
```bash
pytest project/tests/ -m docker        # Docker-related tests
pytest project/tests/ -m integration   # Integration tests
```

See `tests/README.md` for comprehensive testing documentation.

## Documentation

- **Phase 1 PRD**: `docs/prd_phase1.md` - Detailed Phase 1 requirements
- **Testing Guide**: `docs/testing-guide-phase1.md` - Testing procedures
- **Test Suite**: `tests/README.md` - Test suite documentation

