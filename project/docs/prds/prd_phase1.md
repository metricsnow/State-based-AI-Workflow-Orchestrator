# Product Requirements Document: Phase 1 - Foundation & Core Orchestration

**Project**: AI-Powered Workflow Orchestration for Trading Operations  
**Phase**: Phase 1 - Foundation & Core Orchestration  
**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Mission Planner Agent  
**Status**: Draft  
**Parent PRD**: `project/docs/prd.md`

---

## Document Control

- **Phase Name**: Foundation & Core Orchestration
- **Phase Number**: 1
- **Version**: 1.0
- **Author**: Mission Planner Agent
- **Last Updated**: 2025-01-27
- **Status**: Draft
- **Dependencies**: None (Foundation Phase)
- **Duration Estimate**: 2-3 weeks
- **Team Size**: 1-2 developers

---

## Executive Summary

### Phase Vision
Establish the foundational orchestration infrastructure with Apache Airflow and event-driven architecture using Kafka. This phase creates the core data pipeline orchestration capabilities that will serve as the foundation for AI workflow integration in subsequent phases.

### Key Objectives
1. **Airflow Foundation**: Set up Apache Airflow with modern TaskFlow API
2. **Event-Driven Architecture**: Implement Kafka for event streaming and coordination
3. **Development Environment**: Establish local development environment with Docker
4. **Basic Orchestration**: Create working DAGs demonstrating orchestration capabilities

### Success Metrics
- **Airflow Setup**: Webserver accessible, DAGs executing successfully
- **TaskFlow API**: All DAGs use modern TaskFlow patterns
- **Kafka Integration**: Producer/consumer working with event schema defined
- **Development Environment**: All services running locally via Docker Compose

---

## Phase Overview

### Scope
This phase establishes the core orchestration infrastructure:
- Apache Airflow setup and configuration
- TaskFlow API implementation for modern DAG development
- Kafka event streaming setup for event-driven coordination
- Local development environment with Docker Compose

### Out of Scope
- AI workflow integration (Phase 2)
- LangGraph implementation (Phase 2)
- Production deployment (Phase 4)
- Monitoring and observability (Phase 4)

### Phase Dependencies
- **Prerequisites**: Python 3.11+, Docker, Docker Compose, Python virtual environment (venv)
- **External Dependencies**: None
- **Internal Dependencies**: None (Foundation phase)

---

## Technical Architecture

### Phase 1 Architecture

```
┌─────────────────────────────────────┐
│     Local Development Environment   │
│         (Docker Compose)            │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐                  │
│  │   Airflow    │                  │
│  │  Webserver  │                  │
│  │  (Port 8080) │                  │
│  └──────┬───────┘                  │
│         │                           │
│  ┌──────▼───────┐                  │
│  │   Airflow    │                  │
│  │  Scheduler   │                  │
│  └──────┬───────┘                  │
│         │                           │
│  ┌──────▼───────┐                  │
│  │   Airflow    │                  │
│  │   Executor    │                  │
│  └──────┬───────┘                  │
│         │                           │
│         │ Publishes Events          │
│         │                           │
│  ┌──────▼───────┐                  │
│  │    Kafka     │                  │
│  │   (Zookeeper)│                  │
│  │  Port 9092   │                  │
│  └──────────────┘                  │
│                                     │
└─────────────────────────────────────┘
```

### Technology Stack

#### Orchestration Layer
- **Apache Airflow** (Trust Score: 9.1)
  - Version: 2.8.4+ (latest stable)
  - Components: Webserver, Scheduler, Executor
  - Database: PostgreSQL (recommended) or SQLite (development)

#### Event Streaming
- **Apache Kafka** (Trust Score: N/A - Infrastructure)
  - Version: 3.6.0+ (latest stable)
  - Components: Kafka Broker, Zookeeper
  - Port: 9092 (Kafka), 2181 (Zookeeper)

#### Development Environment
- **Docker** & **Docker Compose**
  - Containerization for all services
  - Local development environment

### Data Flow

1. **Airflow DAG Execution**:
   - DAG defined using TaskFlow API (`@dag`, `@task` decorators)
   - Tasks execute in sequence with data passing via XCom
   - Task publishes event to Kafka topic upon completion

2. **Kafka Event Processing**:
   - Producer sends structured events to Kafka topics
   - Consumer (placeholder for Phase 3) will process events
   - Event schema defined for consistency

---

## Detailed Milestones

### Milestone 1.1: Airflow Setup and Basic DAG

**Objective**: Establish Apache Airflow environment with working DAGs

#### Requirements
- Set up Airflow locally using Docker Compose
- Create basic DAG with 3-4 tasks demonstrating orchestration
- Validate task execution and dependencies

#### Technical Specifications

**Airflow Configuration**:
- **Executor**: LocalExecutor (for development)
- **Database**: PostgreSQL (production-ready) or SQLite (quick start)
- **Webserver Port**: 8080
- **Airflow Version**: 2.8.4 or later

**DAG Requirements**:
- At least one DAG with 3-4 tasks
- Tasks demonstrate data extraction, transformation, loading (ETL pattern)
- Tasks execute successfully with proper dependencies
- DAG visible in Airflow UI

**Docker Compose Structure**:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
  
  airflow-webserver:
    image: apache/airflow:2.8.4
    # ... configuration
  
  airflow-scheduler:
    image: apache/airflow:2.8.4
    # ... configuration
```

#### Acceptance Criteria
- [ ] Airflow webserver accessible at `http://localhost:8080`
- [ ] At least one DAG visible in Airflow UI
- [ ] DAG contains 3-4 tasks with clear dependencies
- [ ] All tasks execute successfully when DAG is triggered
- [ ] Task logs accessible and readable
- [ ] DAG can be paused/unpaused via UI

#### Testing Requirements
- **Manual Testing**:
  - Access Airflow UI and verify DAG visibility
  - Trigger DAG execution and verify task completion
  - Verify task dependencies are respected
  - Check task logs for errors

- **Automated Testing**:
  - Unit tests for DAG structure validation
  - Test DAG import and parsing
  - Verify no syntax errors in DAG definitions

#### Dependencies
- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- 4GB+ RAM available for containers

#### Risks and Mitigation
- **Risk**: Airflow setup complexity
  - **Mitigation**: Use official Airflow Docker images, follow official documentation
- **Risk**: Database connection issues
  - **Mitigation**: Use Docker Compose networking, verify environment variables

---

### Milestone 1.2: TaskFlow API Implementation

**Objective**: Migrate to modern TaskFlow API for maintainable, testable DAGs

#### Requirements
- Implement DAGs using TaskFlow API (`@dag`, `@task` decorators)
- Tasks pass data via XCom automatically
- Unit tests validate DAG structure

#### Technical Specifications

**TaskFlow API Pattern**:
```python
from airflow.decorators import dag, task
from datetime import datetime, timezone

@dag(
    dag_id="example_taskflow",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
)
def example_dag():
    @task
    def extract():
        return {"data": [1, 2, 3, 4, 5]}
    
    @task
    def transform(data: dict):
        return {"transformed": [x * 2 for x in data["data"]]}
    
    @task
    def load(transformed_data: dict):
        print(f"Loading: {transformed_data}")
    
    # Automatic dependency management
    extracted = extract()
    transformed = transform(extracted)
    load(transformed)

example_dag()
```

**Key Features**:
- Type hints for data passing
- Automatic XCom management
- Python-native syntax
- Testable functions

#### Acceptance Criteria
- [ ] All DAGs use `@dag` decorator
- [ ] All tasks use `@task` decorator
- [ ] Tasks pass data via function arguments (XCom automatic)
- [ ] Type hints used for data structures
- [ ] Unit tests validate DAG structure
- [ ] Unit tests validate task functions independently
- [ ] DAGs execute successfully with TaskFlow API

#### Testing Requirements
- **Unit Tests**:
  - Test task functions independently (without Airflow)
  - Test DAG structure and task dependencies
  - Test data passing between tasks
  - Mock external dependencies

- **Integration Tests**:
  - Test DAG execution in test environment
  - Verify XCom data passing
  - Validate task execution order

#### Dependencies
- Milestone 1.1 completed (Airflow setup)
- Python typing knowledge
- pytest for testing

#### Risks and Mitigation
- **Risk**: Learning curve for TaskFlow API
  - **Mitigation**: Use official Airflow TaskFlow documentation, start with simple examples
- **Risk**: XCom size limitations
  - **Mitigation**: Use external storage (S3, database) for large data, keep XCom for metadata

---

### Milestone 1.3: Kafka Event Streaming Setup

**Objective**: Establish Kafka infrastructure for event-driven coordination

#### Requirements
- Set up Kafka locally using Docker Compose
- Implement Kafka producer for sending events
- Implement Kafka consumer for processing events
- Define basic event schema

#### Technical Specifications

**Kafka Configuration**:
- **Kafka Version**: 3.6.0+ (latest stable)
- **Zookeeper**: Required for Kafka coordination
- **Ports**: 9092 (Kafka), 2181 (Zookeeper)
- **Topics**: `workflow-events` (default topic)

**Event Schema** (JSON):
```json
{
  "event_id": "uuid",
  "event_type": "workflow.triggered|workflow.completed|workflow.failed",
  "timestamp": "ISO 8601",
  "source": "airflow|langgraph|fastapi",
  "workflow_id": "dag_id or workflow_id",
  "workflow_run_id": "run_id",
  "payload": {
    "data": "workflow-specific data"
  },
  "metadata": {
    "environment": "dev|staging|prod",
    "version": "1.0"
  }
}
```

**Producer Implementation**:
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

event = {
    "event_id": str(uuid.uuid4()),
    "event_type": "workflow.triggered",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "source": "airflow",
    "workflow_id": "example_dag",
    "workflow_run_id": "run_123",
    "payload": {"data": "example"},
    "metadata": {"environment": "dev", "version": "1.0"}
}

producer.send('workflow-events', event)
producer.flush()
```

**Consumer Implementation**:
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'workflow-events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for message in consumer:
    event = message.value
    print(f"Received event: {event['event_type']}")
    # Process event
```

#### Acceptance Criteria
- [ ] Kafka running locally via Docker Compose
- [ ] Zookeeper running and Kafka connected
- [ ] Producer successfully sends events to Kafka topics
- [ ] Consumer successfully receives and processes events
- [ ] Event schema defined and documented
- [ ] Events are JSON-serializable and validated
- [ ] Basic error handling for producer/consumer
- [ ] Kafka topics created and visible

#### Testing Requirements
- **Manual Testing**:
  - Verify Kafka is running (`docker ps`)
  - Send test event via producer
  - Verify consumer receives event
  - Check Kafka topic contents

- **Automated Testing**:
  - Unit tests for event schema validation
  - Integration tests for producer/consumer
  - Test event serialization/deserialization
  - Test error handling

#### Dependencies
- Milestone 1.1 completed (Docker environment)
- Kafka Python client library (`kafka-python`)

#### Risks and Mitigation
- **Risk**: Kafka setup complexity
  - **Mitigation**: Use official Kafka Docker images, follow quickstart guides
- **Risk**: Event schema evolution
  - **Mitigation**: Use versioned event schemas, implement schema registry (future)
- **Risk**: Consumer lag and performance
  - **Mitigation**: Monitor consumer lag, implement proper error handling

---

## Integration Points

### Airflow → Kafka Integration

**Pattern**: Airflow task publishes event to Kafka upon completion

**Implementation**:
```python
from airflow.decorators import task
from kafka import KafkaProducer
import json

@task
def process_data():
    # Process data
    result = {"status": "success", "count": 100}
    
    # Publish event to Kafka
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    event = {
        "event_type": "workflow.completed",
        "source": "airflow",
        "workflow_id": "example_dag",
        "payload": result
    }
    
    producer.send('workflow-events', event)
    producer.flush()
    
    return result
```

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
- Airflow FERNET_KEY
- Database passwords (PostgreSQL, etc.)
- Kafka connection strings
- API keys (if any)
- Secret keys
- Authentication tokens
- Any other sensitive configuration

#### Implementation Pattern:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials from environment
FERNET_KEY = os.getenv('FERNET_KEY')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
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
# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation (should show venv path)
which python  # macOS/Linux
# OR
where python  # Windows
```

**Note**: Always activate venv before running any Python commands, installing packages, or running scripts.

### Docker Compose Structure

```yaml
version: '3.8'

services:
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

  airflow-webserver:
    image: apache/airflow:2.8.4
    depends_on:
      - postgres
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__API__AUTH_BACKEND=airflow.api.auth.backend.basic_auth
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: webserver
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  airflow-scheduler:
    image: apache/airflow:2.8.4
    depends_on:
      - postgres
      - airflow-webserver
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: scheduler

volumes:
  postgres_data:
```

### Environment Variables

Create `.env` file:
```bash
# Airflow
# Ensure venv is activated first
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
AIRFLOW_UID=50000

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

---

## Testing Strategy

### Unit Testing
- **DAG Structure Tests**: Validate DAG definitions, task dependencies
- **Task Function Tests**: Test task logic independently
- **Event Schema Tests**: Validate event structure and serialization

### Integration Testing
- **End-to-End DAG Execution**: Test complete DAG workflows
- **Kafka Integration**: Test producer/consumer communication
- **Docker Compose Testing**: Test service startup and health checks

### Test Framework
- **pytest**: Primary testing framework
- **pytest-airflow**: Airflow-specific testing utilities
- **pytest-docker**: Docker Compose integration for tests

---

## Success Criteria

### Phase 1 Completion Criteria
- [x] All three milestones completed and validated - ✅ Complete
- [x] Airflow webserver accessible and functional - ✅ Complete
- [x] At least 2 DAGs using TaskFlow API - ✅ Complete (2 DAGs implemented)
- [x] Kafka producer/consumer working - ✅ Complete (42 tests passing)
- [x] Event schema defined and documented - ✅ Complete
- [x] Docker Compose environment fully functional - ✅ Complete
- [x] Unit tests passing (>80% coverage) - ✅ Complete (97% coverage achieved)
- [x] Integration tests passing - ✅ Complete (28 integration tests)
- [x] Documentation complete - ✅ Complete (10+ comprehensive guides)

### Quality Gates
- **Code Quality**: PEP8 compliance, type hints, docstrings
- **Test Coverage**: >80% for new code
- **Documentation**: All components documented
- **Performance**: DAGs execute in <1 minute (for test workflows)

---

## Risk Assessment

### Technical Risks

**Risk 1: Airflow Setup Complexity**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Use official Docker images, follow step-by-step guides
- **Contingency**: Use Prefect Cloud free tier as alternative

**Risk 2: Kafka Configuration Issues**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use Confluent Docker images, test with simple producer/consumer
- **Contingency**: Use Redis Pub/Sub as lightweight alternative for development

**Risk 3: TaskFlow API Learning Curve**
- **Probability**: High
- **Impact**: Low
- **Mitigation**: Start with simple examples, reference official documentation
- **Contingency**: Use traditional operators initially, migrate later

### Operational Risks

**Risk 4: Resource Requirements**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Monitor Docker resource usage, optimize container configurations
- **Contingency**: Reduce number of services, use lighter alternatives

---

## Dependencies and Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows with WSL2
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: 8GB+ recommended
- **Disk Space**: 10GB+ for images and data

### Software Dependencies
- Python 3.11+ (for local development)
- Python virtual environment (venv) - always use venv for local development
- Git (for version control)
- IDE/Editor (VS Code, PyCharm, etc.)

### External Dependencies
- None (all services run locally)

---

## Timeline and Effort Estimation

### Milestone Estimates
- **Milestone 1.1**: 3-5 days
- **Milestone 1.2**: 2-3 days
- **Milestone 1.3**: 3-4 days

### Total Phase Estimate
- **Duration**: 2-3 weeks
- **Effort**: 40-60 hours
- **Team**: 1-2 developers

### Critical Path
1. Milestone 1.1 (Airflow Setup) - Foundation
2. Milestone 1.2 (TaskFlow API) - Depends on 1.1
3. Milestone 1.3 (Kafka) - Can run in parallel with 1.2

---

## Deliverables

### Code Deliverables
- [x] Docker Compose configuration (TASK-001) - ✅ Complete
- [x] Test suite with modular structure (TASK-001) - ✅ Complete
- [x] Airflow DAGs using TaskFlow API (TASK-003, TASK-005) - ✅ Complete
  - 2 DAGs implemented: `example_etl_dag.py`, `xcom_data_passing_dag.py`
- [x] Kafka producer/consumer implementations (TASK-011, TASK-012) - ✅ Complete
  - Producer: WorkflowEventProducer class with 17 tests
  - Consumer: WorkflowEventConsumer class with 25 tests
- [x] Unit tests (TASK-004, TASK-007) - ✅ Complete (108 tests, 97% coverage)
- [x] Integration tests (TASK-008, TASK-013) - ✅ Complete
  - 13 DAG execution tests (TASK-008)
  - 15 Airflow-Kafka integration tests (TASK-013)
- [x] Event schema definitions (TASK-010) - ✅ Complete
  - Pydantic models with validation, 26 tests

### Documentation Deliverables
- [x] Phase 1 PRD (this document) - ✅ Complete
- [x] Setup guide for development environment (`docs/setup-guide.md`) - ✅ Complete
- [x] Testing guide (`docs/testing-guide-phase1.md`) - ✅ Complete
- [x] Test suite documentation (`tests/README.md`) - ✅ Complete
- [x] DAG development guide (`docs/taskflow-api-guide.md`) - ✅ Complete
  - TaskFlow API implementation guide (TASK-005)
- [x] Event schema documentation (`docs/event-schema-guide.md`) - ✅ Complete
- [x] Kafka producer guide (`docs/kafka-producer-guide.md`) - ✅ Complete
- [x] Kafka consumer guide (`docs/kafka-consumer-guide.md`) - ✅ Complete
- [x] Kafka setup guide (`docs/kafka-setup-guide.md`) - ✅ Complete
- [x] Airflow-Kafka integration guide (`docs/airflow-kafka-integration-guide.md`) - ✅ Complete

### Configuration Deliverables
- [x] `.env.example` file - ✅ Complete
- [x] `docker-compose.yml` - ✅ Complete
- [x] `.env` file (with FERNET_KEY) - ✅ Complete
- [x] Airflow configuration files (TASK-002) - ✅ Complete
  - Environment variables configured in docker-compose.yml
  - FERNET_KEY, database connection, executor settings
- [x] Kafka topic configurations (TASK-009) - ✅ Complete
  - Default topic 'workflow-events' configured
  - Kafka and Zookeeper fully operational

---

## Next Phase Preview

**Phase 2: AI Workflow Foundation** will build upon Phase 1 by:
- Implementing LangGraph stateful workflows
- Creating multi-agent systems
- Integrating with Kafka events from Phase 1
- Setting up local LLM deployment (Ollama)

**Prerequisites for Phase 2**:
- Phase 1 completed and validated
- Kafka events flowing successfully
- Understanding of event-driven patterns

---

## Appendix

### A. Event Schema Reference

See main PRD for complete event schema definition.

### B. Airflow TaskFlow API Examples

See MCP Context7 documentation for official TaskFlow API patterns.

### C. Kafka Best Practices

- Use idempotent producers for exactly-once semantics
- Implement proper error handling and retries
- Monitor consumer lag
- Use appropriate partition keys for event ordering

---

**PRD Phase 1 Version**: 1.0  
**Last Updated**: 2025-01-27  
**Next Review**: Upon Phase 1 completion

