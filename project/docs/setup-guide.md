# Setup Guide: Phase 1 - Foundation & Core Orchestration

## Overview

This guide provides step-by-step instructions for setting up the Phase 1 development environment.

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows with WSL2
- **Docker**: 20.10+ installed and running
- **Docker Compose**: 2.0+ installed
- **Python**: 3.11+ (for local development)
- **RAM**: 8GB+ recommended
- **Disk Space**: 10GB+ for images and data

### Verify Prerequisites

```bash
# Check Docker
docker --version
docker ps

# Check Docker Compose
docker-compose --version

# Check Python
python3 --version  # Should be 3.11+
```

## Step-by-Step Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd Project2
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Verify activation
which python  # Should show venv path
```

### Step 3: Generate FERNET_KEY

```bash
# Ensure venv is activated
source venv/bin/activate

# Install cryptography if needed
pip install cryptography

# Generate FERNET_KEY
./scripts/generate-fernet-key.sh
```

Copy the generated FERNET_KEY.

### Step 4: Create .env File

```bash
# Create .env file from example
cp .env.example .env

# Edit .env and add the generated FERNET_KEY
# FERNET_KEY=your_generated_key_here
```

**Important**: The `.env` file is in `.gitignore` and will not be committed to version control.

### Step 5: Verify Configuration

Run pre-flight tests:

```bash
# Option 1: Pytest (recommended)
source venv/bin/activate
pip install -r project/tests/infrastructure/requirements-test.txt
pytest project/tests/infrastructure/test_docker_compose.py -v

# Option 2: Shell script
./scripts/test-docker-compose.sh
```

**Expected**: All 11 configuration tests should pass.

### Step 6: Start Docker Compose Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Wait for services to be healthy** (2-3 minutes):
- PostgreSQL: `healthy`
- Zookeeper: `healthy`
- Kafka: `healthy`
- Airflow Webserver: `healthy`
- Airflow Scheduler: `running`

### Step 7: Verify Services

```bash
# Check Airflow UI
curl http://localhost:8080/health
# Or open in browser: http://localhost:8080

# Check Kafka
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check PostgreSQL
docker-compose exec postgres pg_isready -U airflow
```

### Step 8: Run Integration Tests (Optional)

```bash
# Ensure services are running
docker-compose ps

# Run integration tests
pytest project/tests/infrastructure/ -m integration -v
```

## Directory Structure

After setup, your project structure should be:

```
.
├── docker-compose.yml          # Docker Compose configuration
├── .env                        # Environment variables (created)
├── .env.example               # Environment template
├── pytest.ini                  # Pytest configuration
├── venv/                       # Python virtual environment
├── scripts/                    # Utility scripts
│   ├── generate-fernet-key.sh
│   └── test-docker-compose.sh
└── project/
    ├── dags/                   # Airflow DAGs (empty initially)
    ├── logs/                   # Airflow logs
    ├── plugins/                # Airflow plugins
    ├── tests/                  # Test suite
    │   └── infrastructure/     # Infrastructure tests
    └── docs/                   # Documentation
```

## Accessing Services

### Airflow Webserver
- **URL**: http://localhost:8080
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin` (change in production)

### Kafka
- **Bootstrap Server**: `localhost:9092`
- **Zookeeper**: `localhost:2181`

### PostgreSQL
- **Host**: `postgres` (from within Docker network)
- **Port**: `5432` (internal)
- **Database**: `airflow`
- **User**: `airflow`
- **Password**: `airflow` (from docker-compose.yml)

## Troubleshooting

### Services Not Starting

1. **Check Docker daemon**:
   ```bash
   docker ps
   ```

2. **Check port conflicts**:
   ```bash
   lsof -i :8080  # Airflow
   lsof -i :9092  # Kafka
   ```

3. **Check logs**:
   ```bash
   docker-compose logs <service-name>
   ```

### FERNET_KEY Issues

1. **Regenerate FERNET_KEY**:
   ```bash
   source venv/bin/activate
   ./scripts/generate-fernet-key.sh
   ```

2. **Update .env file** with new key

3. **Restart services**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Test Failures

1. **Install test dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r project/tests/infrastructure/requirements-test.txt
   ```

2. **Check .env file exists**:
   ```bash
   ls -la .env
   ```

3. **Verify Docker Compose syntax**:
   ```bash
   docker-compose config
   ```

## Next Steps

After successful setup:

1. ✅ **TASK-001 Complete**: Docker Compose environment setup
2. **TASK-002**: Airflow Configuration and Initialization
3. **TASK-003**: Basic DAG Creation
4. **TASK-004**: DAG Validation and Testing

See `project/dev/tasks/` for task details.

## Security Notes

⚠️ **IMPORTANT**: 
- `.env` file contains sensitive credentials and is in `.gitignore`
- Never commit `.env` file to version control
- Change default passwords in production
- Use strong FERNET_KEY in production
- All credentials MUST be in `.env` file (MANDATORY requirement)

## Documentation

- **Phase 1 PRD**: `project/docs/prd_phase1.md`
- **Testing Guide**: `project/docs/testing-guide-phase1.md`
- **Test Suite**: `project/tests/README.md`
- **Task Details**: `project/dev/tasks/TASK-001.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test logs: `docker-compose logs`
3. Check test output: `pytest project/tests/infrastructure/ -v`
4. Review task documentation: `project/dev/tasks/TASK-001.md`

