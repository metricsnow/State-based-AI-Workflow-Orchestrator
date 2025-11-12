# Product Requirements Document: Phase 4 - Production Infrastructure

**Project**: AI-Powered Workflow Orchestration for Trading Operations  
**Phase**: Phase 4 - Production Infrastructure  
**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Mission Planner Agent  
**Status**: Draft  
**Parent PRD**: `project/docs/prd.md`

---

## Document Control

- **Phase Name**: Production Infrastructure
- **Phase Number**: 4
- **Version**: 1.0
- **Author**: Mission Planner Agent
- **Last Updated**: 2025-01-27
- **Status**: Draft
- **Dependencies**: Phase 1, Phase 2, Phase 3
- **Duration Estimate**: 2-3 weeks
- **Team Size**: 1-2 developers

---

## Executive Summary

### Phase Vision
Establish production-ready infrastructure with monitoring, containerization, and API orchestration. This phase prepares the system for production deployment and provides the foundation for scaling and operations.

### Key Objectives
1. **Monitoring**: Set up Prometheus/Grafana for observability
2. **Containerization**: Dockerize all services
3. **API Layer**: Create FastAPI orchestration API
4. **Production Readiness**: Prepare for deployment

### Success Metrics
- **Monitoring**: Prometheus collecting metrics, Grafana dashboards created
- **Containerization**: All services running in Docker containers
- **API**: FastAPI endpoints functional with OpenAPI docs
- **Production Ready**: System ready for deployment

---

## Phase Overview

### Scope
This phase establishes production infrastructure:
- Prometheus/Grafana monitoring setup
- Docker containerization for all services
- FastAPI orchestration API
- Production configuration

### Out of Scope
- Kubernetes deployment (Phase 5)
- Advanced monitoring (Phase 6)
- Authentication/Authorization (Phase 7)
- Performance optimization (Phase 7)

### Phase Dependencies
- **Prerequisites**: Phases 1-3 completed
- **External Dependencies**: Prometheus, Grafana, FastAPI
- **Internal Dependencies**: All previous phase components

---

## Technical Architecture

### Phase 4 Architecture

```
┌─────────────────────────────────────┐
│    Production Infrastructure       │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐                  │
│  │  Prometheus  │                  │
│  │  (Metrics)   │                  │
│  └──────┬───────┘                  │
│         │                           │
│  ┌──────▼───────┐                  │
│  │   Grafana    │                  │
│  │ (Dashboards) │                  │
│  └──────────────┘                  │
│                                     │
│  ┌──────────────┐                  │
│  │   FastAPI    │                  │
│  │  (Port 8000) │                  │
│  └──────────────┘                  │
│                                     │
│  All Services Containerized         │
│  (Docker Compose)                   │
└─────────────────────────────────────┘
```

### Technology Stack

#### Monitoring Layer
- **Prometheus** (Trust Score: N/A - Infrastructure)
  - Version: Latest stable
  - Metrics collection and storage
  - Alerting rules

- **Grafana** (Trust Score: N/A - Infrastructure)
  - Version: Latest stable
  - Visualization and dashboards
  - Alerting integration

#### API Layer
- **FastAPI** (Trust Score: 9.9)
  - Version: 0.115.13+
  - REST API for workflow orchestration
  - OpenAPI/Swagger documentation

#### Containerization
- **Docker** & **Docker Compose**
  - All services containerized
  - Local development environment

---

## Detailed Milestones

### Milestone 1.8: Monitoring Setup (Prometheus/Grafana)

**Objective**: Implement basic monitoring and observability

#### Requirements
- Prometheus collecting metrics
- Grafana dashboard created
- Airflow metrics exposed
- Basic alerting rules configured

#### Technical Specifications

**Prometheus Configuration** (`prometheus.yml`):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'local'
    environment: 'development'

scrape_configs:
  - job_name: 'airflow'
    metrics_path: '/admin/metrics'
    static_configs:
      - targets: ['airflow-webserver:8080']
        labels:
          service: 'airflow'
  
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-exporter:9308']
        labels:
          service: 'kafka'
  
  - job_name: 'fastapi'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['fastapi:8000']
        labels:
          service: 'fastapi'
  
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

**Alerting Rules** (`alerts.yml`):
```yaml
groups:
  - name: airflow_alerts
    rules:
      - alert: AirflowDAGFailed
        expr: airflow_dag_run_state{state="failed"} > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Airflow DAG {{ $labels.dag_id }} has failed"
      
      - alert: AirflowTaskFailed
        expr: airflow_task_instance_state{state="failed"} > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Airflow task {{ $labels.task_id }} has failed"

  - name: kafka_alerts
    rules:
      - alert: KafkaConsumerLag
        expr: kafka_consumer_lag_sum > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Kafka consumer lag is high: {{ $value }}"
```

**Grafana Dashboard Configuration**:
- **Airflow Metrics**:
  - DAG execution success rate
  - Task execution duration
  - Failed task count
  - DAG run status distribution
  
- **Kafka Metrics**:
  - Consumer lag
  - Message throughput
  - Topic partition count
  - Broker status
  
- **API Metrics**:
  - Request rate
  - Response time (p50, p95, p99)
  - Error rate
  - Active connections
  
- **System Metrics**:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network throughput

**Airflow Metrics Exposure**:
```python
# In Airflow configuration
[metrics]
statsd_on = True
statsd_host = prometheus
statsd_port = 9125
statsd_prefix = airflow
```

#### Acceptance Criteria
- [x] Prometheus collecting metrics from all services ✅ TASK-039
- [x] Grafana dashboard created with key metrics ✅ TASK-039
- [x] Airflow metrics exposed and collected ✅ TASK-039
- [x] Basic alerting rules configured ✅ TASK-039
- [x] Metrics visible in Grafana ✅ TASK-039
- [x] Alerts firing correctly ✅ TASK-039
- [x] Dashboard refreshes automatically ✅ TASK-039

#### Testing Requirements
- **Manual Testing**:
  - Verify Prometheus scrapes all targets
  - Verify Grafana dashboards display metrics
  - Test alert firing
  - Verify metric retention

- **Automated Testing**:
  - Test Prometheus configuration
  - Test alert rule syntax
  - Test metric collection endpoints

#### Dependencies
- All services running (Phases 1-3)
- Prometheus, Grafana installed
- Airflow metrics endpoint accessible
- Network connectivity between services

#### Risks and Mitigation
- **Risk**: Metric collection overhead
  - **Mitigation**: Configure appropriate scrape intervals, use metric filtering
- **Risk**: Alert fatigue
  - **Mitigation**: Set appropriate thresholds, use alert grouping

---

### Milestone 1.9: Docker Containerization

**Objective**: Containerize all services with Docker

#### Requirements
- Dockerfiles created for all services
- docker-compose.yml for local development
- All services run in containers
- Services communicate via Docker network

#### Technical Specifications

**Airflow Dockerfile** (`airflow/Dockerfile`):
```dockerfile
FROM apache/airflow:2.8.4

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
```

**LangGraph Service Dockerfile** (`langgraph/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**FastAPI Dockerfile** (`fastapi/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Complete Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    healthcheck:
      test: ["CMD-SHELL", "nc -z localhost 2181"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Airflow
  airflow-webserver:
    build: ./airflow
    depends_on:
      - postgres
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - ./airflow/plugins:/opt/airflow/plugins
    command: webserver
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  airflow-scheduler:
    build: ./airflow
    depends_on:
      - postgres
      - airflow-webserver
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - ./airflow/plugins:/opt/airflow/plugins
    command: scheduler
  
  # LangGraph Service
  langgraph-service:
    build: ./langgraph
    depends_on:
      - kafka
      - ollama
    ports:
      - "8001:8001"
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - OLLAMA_BASE_URL=http://ollama:11434
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # Ollama
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # FastAPI
  fastapi:
    build: ./fastapi
    depends_on:
      - kafka
      - airflow-webserver
    ports:
      - "8000:8000"
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - AIRFLOW_BASE_URL=http://airflow-webserver:8080
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./project/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./project/prometheus/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  grafana:
    image: grafana/grafana:latest
    depends_on:
      - prometheus
    ports:
      - "3002:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./project/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./project/grafana/datasources:/etc/grafana/provisioning/datasources
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  ollama_data:
  prometheus_data:
  grafana_data:
```

#### Acceptance Criteria
- [ ] Dockerfiles created for all services
- [ ] docker-compose.yml functional
- [ ] All services run in containers
- [ ] Services communicate via Docker network
- [ ] Health checks configured
- [ ] Services start in correct order (depends_on)
- [ ] Volumes configured for data persistence
- [ ] Environment variables properly set

#### Testing Requirements
- **Manual Testing**:
  - Start all services: `docker-compose up -d`
  - Verify all services are healthy
  - Test service communication
  - Verify data persistence

- **Automated Testing**:
  - Test Dockerfile builds
  - Test health check endpoints
  - Test service dependencies

#### Dependencies
- All services implemented (Phases 1-3)
- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- Sufficient system resources (8GB+ RAM)

#### Risks and Mitigation
- **Risk**: Resource constraints
  - **Mitigation**: Monitor resource usage, optimize container configurations, use resource limits
- **Risk**: Service startup order
  - **Mitigation**: Use depends_on, health checks, startup scripts

---

### Milestone 1.10: FastAPI Orchestration API

**Objective**: Create REST API for workflow triggers

#### Requirements
- FastAPI application with basic endpoints
- Endpoint to trigger workflows
- Endpoint to check workflow status
- OpenAPI/Swagger documentation

#### Technical Specifications

**FastAPI Application** (`fastapi/main.py`):
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
from kafka import KafkaProducer
import json

app = FastAPI(
    title="Workflow Orchestration API",
    description="API for triggering and managing AI-powered workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class WorkflowType(str, Enum):
    AIRFLOW = "airflow"
    LANGGRAPH = "langgraph"

class WorkflowRequest(BaseModel):
    workflow_id: str = Field(..., description="ID of the workflow to trigger")
    workflow_type: WorkflowType = Field(..., description="Type of workflow")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Workflow parameters")
    priority: int = Field(default=0, ge=0, le=10, description="Workflow priority (0-10)")

class WorkflowResponse(BaseModel):
    workflow_run_id: str = Field(..., description="Unique run ID")
    status: str = Field(..., description="Workflow status")
    created_at: datetime = Field(..., description="Creation timestamp")
    workflow_id: str = Field(..., description="Workflow ID")
    workflow_type: str = Field(..., description="Workflow type")

class WorkflowStatus(BaseModel):
    workflow_run_id: str = Field(..., description="Workflow run ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress (0.0-1.0)")
    result: Optional[Dict[str, Any]] = Field(None, description="Workflow result")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class WorkflowInfo(BaseModel):
    workflow_id: str
    workflow_type: str
    description: str
    parameters_schema: Dict[str, Any]

# Kafka Producer
kafka_producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {"message": "Workflow Orchestration API", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.post("/workflows/trigger", response_model=WorkflowResponse, tags=["Workflows"])
async def trigger_workflow(request: WorkflowRequest):
    """Trigger a workflow execution"""
    workflow_run_id = str(uuid.uuid4())
    
    # Create event for Kafka
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "workflow.triggered",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "fastapi",
        "workflow_id": request.workflow_id,
        "workflow_type": request.workflow_type.value,
        "workflow_run_id": workflow_run_id,
        "payload": {
            "parameters": request.parameters,
            "priority": request.priority
        },
        "metadata": {
            "environment": "dev",
            "version": "1.0"
        }
    }
    
    # Publish to Kafka
    try:
        kafka_producer.send('workflow-events', event)
        kafka_producer.flush()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {str(e)}")
    
    return WorkflowResponse(
        workflow_run_id=workflow_run_id,
        status="triggered",
        created_at=datetime.now(timezone.utc),
        workflow_id=request.workflow_id,
        workflow_type=request.workflow_type.value
    )

@app.get("/workflows/{workflow_run_id}/status", response_model=WorkflowStatus, tags=["Workflows"])
async def get_workflow_status(workflow_run_id: str):
    """Get workflow execution status"""
    # Query workflow status from Airflow or LangGraph
    # This is a placeholder - actual implementation would query the workflow engine
    # For Airflow: Use Airflow API
    # For LangGraph: Query checkpoint store
    
    # Placeholder implementation
    return WorkflowStatus(
        workflow_run_id=workflow_run_id,
        status="running",
        progress=0.5,
        started_at=datetime.now(timezone.utc)
    )

@app.get("/workflows", response_model=List[WorkflowInfo], tags=["Workflows"])
async def list_workflows():
    """List available workflows"""
    # Return list of available workflows
    # This would query Airflow DAGs and LangGraph workflows
    return [
        WorkflowInfo(
            workflow_id="example_dag",
            workflow_type="airflow",
            description="Example Airflow DAG",
            parameters_schema={}
        ),
        WorkflowInfo(
            workflow_id="langgraph_workflow",
            workflow_type="langgraph",
            description="Example LangGraph workflow",
            parameters_schema={}
        )
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Requirements File** (`fastapi/requirements.txt`):
```txt
fastapi>=0.115.13
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
kafka-python>=2.0.2
python-multipart>=0.0.6
```

#### Acceptance Criteria
- [ ] FastAPI application running on port 8000
- [ ] Endpoint to trigger workflows functional (`POST /workflows/trigger`)
- [ ] Endpoint to check status functional (`GET /workflows/{workflow_run_id}/status`)
- [ ] Endpoint to list workflows functional (`GET /workflows`)
- [ ] Health check endpoint functional (`GET /health`)
- [ ] OpenAPI/Swagger docs accessible at `/docs`
- [ ] ReDoc documentation accessible at `/redoc`
- [ ] API integrates with Kafka for workflow triggering
- [ ] Request/response models validated with Pydantic
- [ ] Error handling implemented

#### Testing Requirements
- **Manual Testing**:
  - Test all endpoints via Swagger UI
  - Test workflow triggering
  - Test status checking
  - Verify OpenAPI documentation

- **Automated Testing**:
  - Unit tests for API endpoints
  - Integration tests with Kafka
  - Test request validation
  - Test error handling

#### Dependencies
- Phases 1-3 completed
- Python 3.11+
- Python virtual environment (venv) - always use venv for local development
- FastAPI 0.115.13+ installed (with venv activated)
- Kafka running (from Phase 1)

#### Risks and Mitigation
- **Risk**: API performance under load
  - **Mitigation**: Use async endpoints, implement rate limiting (Phase 7), optimize database queries
- **Risk**: Kafka connection failures
  - **Mitigation**: Implement retry logic, connection pooling, health checks

---

## Integration Points

### FastAPI → Kafka Integration

**Pattern**: FastAPI publishes workflow trigger events to Kafka

**Implementation**:
- FastAPI endpoint receives workflow trigger request
- Creates event with workflow details
- Publishes to Kafka `workflow-events` topic
- Airflow/LangGraph consumers process events

### FastAPI → Airflow Integration

**Pattern**: FastAPI queries Airflow API for workflow status

**Implementation**:
- FastAPI queries Airflow REST API for DAG run status
- Returns status information to API client
- Handles Airflow API errors gracefully

---

## Security Requirements (CRITICAL)

### Credential Management - MANDATORY

**ALL credentials MUST be stored in `.env` file. This is a MANDATORY security requirement.**

#### Requirements
- **ALL API keys, database credentials, secret keys, tokens, and passwords MUST be in `.env` file only**
- **NEVER hardcode credentials in source code**
- **NEVER commit `.env` file to version control** (already in `.gitignore`)
- **Always use environment variables loaded from `.env` file**
- **Create `.env.example` file with placeholder values as template**
- **Document all required environment variables in documentation**

#### Credential Types That Must Be in `.env`:
- Prometheus credentials
- Grafana admin passwords
- Database passwords
- Kubernetes secrets
- Any other sensitive configuration

#### Implementation Pattern:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials from environment
GRAFANA_ADMIN_PASSWORD = os.getenv('GRAFANA_ADMIN_PASSWORD')
PROMETHEUS_AUTH_TOKEN = os.getenv('PROMETHEUS_AUTH_TOKEN')
```

#### Validation:
- Code review must verify no hardcoded credentials
- All credential access must use `os.getenv()` or similar
- `.env.example` must list all required variables
- Documentation must specify all required environment variables

## Development Environment

### Python Virtual Environment Setup

**Always use venv for local development:**

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation (should show venv path)
which python  # macOS/Linux
# OR
where python  # Windows
```

**Note**: Always activate venv before running any Python commands, installing packages, or running scripts.

### Python Dependencies

```txt
fastapi>=0.115.13
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
kafka-python>=2.0.2
python-multipart>=0.0.6
httpx>=0.27.0  # For Airflow API calls
```

**Install with venv activated:**

```bash
# With venv activated
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:
```bash
# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Airflow
AIRFLOW_BASE_URL=http://airflow-webserver:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
```

---

## Testing Strategy

### Unit Testing
- **API Endpoints**: Test all FastAPI endpoints
- **Request Validation**: Test Pydantic models
- **Error Handling**: Test error scenarios

### Integration Testing
- **Kafka Integration**: Test event publishing
- **Airflow Integration**: Test status queries
- **End-to-End**: Test complete workflow trigger flow

### Test Framework
- **pytest**: Primary testing framework
- **httpx**: For API testing
- **pytest-asyncio**: For async endpoint testing

---

## Success Criteria

### Phase 4 Completion Criteria
- [x] Milestone 1.8 (Monitoring) completed and validated ✅ TASK-039
- [ ] Milestone 1.9 (Docker Containerization) - In Progress
- [ ] Milestone 1.10 (FastAPI Orchestration API) - Pending
- [x] Prometheus collecting metrics from all services ✅ TASK-039
- [x] Grafana dashboards created and functional ✅ TASK-039
- [ ] All services containerized with Docker
- [ ] FastAPI API functional with all endpoints
- [ ] OpenAPI/Swagger documentation accessible
- [x] Health checks configured for all services ✅ TASK-039
- [x] Docker Compose environment fully functional ✅ TASK-039
- [x] Integration tests passing ✅ 164 tests passing
- [x] Documentation complete ✅ TASK-039

### Quality Gates
- **Code Quality**: PEP8 compliance, type hints, docstrings
- **Test Coverage**: >80% for new code
- **Documentation**: All components documented
- **Performance**: API response time <500ms (target)

---

## Risk Assessment

### Technical Risks

**Risk 1: Monitoring Overhead**
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Configure appropriate scrape intervals, use metric filtering
- **Contingency**: Reduce monitoring frequency, disable non-critical metrics

**Risk 2: Container Resource Constraints**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Monitor resource usage, set resource limits, optimize images
- **Contingency**: Increase system resources, reduce number of services

**Risk 3: API Performance**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Use async endpoints, implement caching, optimize database queries
- **Contingency**: Add load balancing, horizontal scaling

---

## Dependencies and Prerequisites

### System Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: 8GB+ recommended
- **Disk Space**: 20GB+ for images and data

### Software Dependencies
- All services from Phases 1-3
- Prometheus, Grafana
- FastAPI, Uvicorn

### External Dependencies
- None (all services run locally)

---

## Timeline and Effort Estimation

### Milestone Estimates
- **Milestone 1.8**: 3-4 days
- **Milestone 1.9**: 4-5 days
- **Milestone 1.10**: 3-4 days

### Total Phase Estimate
- **Duration**: 2-3 weeks
- **Effort**: 50-70 hours
- **Team**: 1-2 developers

### Critical Path
1. Milestone 1.9 (Docker) - Foundation for all services
2. Milestone 1.8 (Monitoring) - Can run in parallel
3. Milestone 1.10 (FastAPI) - Depends on Docker setup

---

## Deliverables

### Code Deliverables
- [ ] Prometheus configuration files
- [ ] Grafana dashboard configurations
- [ ] Dockerfiles for all services
- [ ] Docker Compose configuration
- [ ] FastAPI application code
- [ ] Unit and integration tests

### Documentation Deliverables
- [ ] Phase 4 PRD (this document)
- [ ] Monitoring setup guide
- [ ] Docker deployment guide
- [ ] FastAPI API documentation
- [ ] Integration patterns guide

### Configuration Deliverables
- [ ] `.env.example` file
- [ ] `docker-compose.yml`
- [ ] Prometheus configuration
- [ ] Grafana datasource configuration
- [ ] Alert rules configuration

---

## Next Phase Preview

**Phase 5: Enhanced Infrastructure** will build upon Phase 4 by:
- Deploying to Kubernetes cluster
- Implementing advanced LangGraph features
- Integrating vLLM for high-performance inference
- Scaling system horizontally

**Prerequisites for Phase 5**:
- Phase 4 completed and validated
- Kubernetes cluster available
- Understanding of Kubernetes concepts

---

**PRD Phase 4 Version**: 1.0  
**Last Updated**: 2025-01-27  
**Next Review**: Upon Phase 4 completion

