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
- Ollama: `healthy` (after 40s start_period)

### Step 7: Initialize Airflow

**IMPORTANT**: Airflow database must be initialized before accessing the UI.

```bash
# Run Airflow initialization script
./scripts/init-airflow.sh
```

This script will:
- Wait for PostgreSQL to be ready
- Initialize Airflow database schema
- Create admin user (username: `admin`, password: `admin`)
- Verify Airflow configuration
- Test Airflow CLI commands

**Expected Output**:
```
[INFO] PostgreSQL is ready!
[INFO] Initializing Airflow database...
Initialization done
[INFO] Airflow database initialized successfully!
[INFO] Checking if admin user exists...
[INFO] Admin user created successfully! (or [WARN] Admin user already exists)
[INFO] Airflow CLI is working correctly
2.8.4
[INFO] Airflow initialization complete!
```

**Note**: 
- If you see warnings about database already being initialized or user already existing, that's normal for subsequent runs
- The script uses `docker-compose run --rm` which creates one-off containers for initialization
- This allows initialization even if the webserver service isn't running yet

### Step 8: Verify Services

```bash
# Check Airflow UI health
curl http://localhost:8080/health
# Or open in browser: http://localhost:8080

# Check Kafka
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check PostgreSQL
docker-compose exec postgres pg_isready -U airflow

# Verify Airflow admin user
docker-compose exec airflow-webserver airflow users list
```

### Step 9: Access Airflow UI

1. **Open browser**: http://localhost:8080
2. **Login with**:
   - Username: `admin`
   - Password: `admin`
3. **Verify**:
   - No errors in UI
   - DAGs list is visible (should show `example_etl_dag`)
   - Scheduler is running
   - Example DAG `example_etl_dag` is available (paused by default)

⚠️ **Security**: Change the admin password in production!

### Step 10: Run Integration Tests (Optional)

```bash
# Ensure services are running
docker-compose ps

# Run integration tests
pytest project/tests/infrastructure/ -m integration -v
```

**Important**: All tests run against the **production environment** - **NEVER with placeholders or mocks**.
- Tests use **real Docker containers** from `docker-compose.yml`
- Tests connect to **actual services** (PostgreSQL, Kafka, Airflow)
- Tests validate **real database connections** (PostgreSQL, not SQLite)
- **No placeholders. No mocks. Production environment only.**

See [Testing Guide](testing-guide-phase1.md) for complete testing procedures.

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
│   ├── init-airflow.sh         # Airflow initialization script
│   └── test-docker-compose.sh
└── project/
    ├── dags/                   # Airflow DAGs
    │   └── example_etl_dag.py  # Example ETL DAG (TASK-003)
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

### Ollama
- **Host**: `ollama` (from within Docker network) or `localhost` (from host)
- **Port**: `11434` (API port)
- **API Endpoint**: `http://ollama:11434` (from containers) or `http://localhost:11434` (from host)
- **Volume**: `ollama_data` (persists models at `/root/.ollama`)
- **Health Check**: Monitors `/api/tags` endpoint
- **Usage**: 
  ```bash
  # From host
  curl http://localhost:11434/api/tags
  
  # From Airflow container
  docker exec airflow-webserver curl http://ollama:11434/api/tags
  
  # Pull a model
  docker exec airflow-ollama ollama pull llama2
  ```

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
   lsof -i :11434 # Ollama
   ```
   
   **Note**: If you have a native Ollama service running, stop it before starting the Docker service:
   ```bash
   # Check for native Ollama
   ps aux | grep ollama
   # Stop native service if needed
   kill <ollama-pid>
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

### Airflow Initialization Issues

1. **Database not initialized**:
   ```bash
   # Run initialization script
   ./scripts/init-airflow.sh
   ```

2. **Admin user creation fails**:
   - Check if user already exists: `docker-compose run --rm airflow-webserver airflow users list`
   - If user exists, script will skip creation (this is normal)

3. **Webserver won't start**:
   - Ensure database is initialized first: `./scripts/init-airflow.sh`
   - Check logs: `docker-compose logs airflow-webserver`
   - Verify PostgreSQL is healthy: `docker-compose ps postgres`

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
2. ✅ **TASK-002 Complete**: Airflow Configuration and Initialization
3. ✅ **TASK-003 Complete**: Basic DAG Creation with Traditional Operators
   - Example DAG `example_etl_dag` is available in Airflow UI
   - DAG demonstrates ETL pattern with XCom data passing
   - Located at: `project/dags/example_etl_dag.py`
4. ✅ **TASK-025 Complete**: Ollama Service Docker Integration
   - Ollama service available in Docker Compose
   - Accessible from Airflow and other containers via `airflow-network`
   - Volume persistence configured for model storage
   - Health checks configured and monitoring
5. **TASK-004**: DAG Validation and Testing (Next)
6. **TASK-005**: Migrate DAGs to TaskFlow API

See `project/dev/tasks/` for task details.

### Testing the Example DAG

After setup, you can test the example DAG:

1. **Access Airflow UI**: http://localhost:8080 (admin/admin)
2. **Find DAG**: Look for `example_etl_dag` in the DAG list
3. **Unpause DAG**: Toggle the pause/unpause switch
4. **Trigger DAG**: Click "Trigger DAG" to run manually
5. **Monitor Execution**: View task execution in Graph View
6. **Check Logs**: View task logs and XCom values

For DAG validation tests, see `project/tests/airflow/test_dag_structure.py`.

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

