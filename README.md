# State-based AI Workflow Orchestrator

**AI-Powered Workflow Orchestration for Trading Operations**

## Overview

This project is an AI-powered workflow orchestration system designed specifically for trading operations, combining the reliability of traditional data pipeline orchestration with the intelligence of modern AI agent workflows. The system addresses the common challenge of workflow fragmentation by integrating Apache Airflow for robust data pipeline management with LangGraph for stateful AI agent workflows, creating a unified platform that can handle both structured data processing and intelligent decision-making.

The architecture is built on an event-driven foundation using Apache Kafka, which enables seamless coordination between traditional orchestration tasks and AI-powered workflows. Airflow manages scheduled data pipelines, ETL processes, and workflow dependencies, while publishing workflow events to Kafka. These events trigger LangGraph stateful agent workflows that can make intelligent decisions, coordinate multi-agent systems, and process complex scenarios that require AI reasoning. This decoupled, event-driven approach ensures that each component can scale independently while maintaining loose coupling and high reliability.

Currently in Phase 1, the system has established the foundational infrastructure with Airflow TaskFlow API for modern DAG development, Kafka for event streaming, and comprehensive event schema validation using Pydantic. The system is production-ready with 176 passing tests, 97% code coverage, and complete documentation. Future phases will integrate LangGraph for AI workflows, local LLM deployment with Ollama, and production infrastructure with Kubernetes, ultimately creating a complete intelligent orchestration platform that can automate complex trading operations workflows with both reliability and intelligence.

- **TaskFlow API**: Modern Airflow DAG development with automatic XCom management and type hints
- **Event-Driven Architecture**: Decoupled components communicate via Kafka events for scalability
- **Type Safety**: Comprehensive type hints and Pydantic validation for runtime safety
- **Test Coverage**: 97% code coverage with 176 tests covering all components
- **Containerization**: Docker Compose for consistent development and deployment environments
- **Documentation**: Comprehensive guides for all components with code examples
- **Error Handling**: Graceful degradation - Kafka failures don't break Airflow tasks
- **Code Quality**: PEP8 compliance, docstrings, and modular architecture

## Technology Stack Overview

### Orchestration Layer

**Apache Airflow 2.8.4**
- **Why**: Industry-standard workflow orchestration platform with mature ecosystem
- **Purpose**: Manages complex data pipelines with scheduling, retries, and monitoring
- **Key Features**: TaskFlow API for modern Python-native DAG development, automatic XCom management, comprehensive UI
- **Components**: Webserver (UI), Scheduler (execution), Executor (task execution)

**PostgreSQL 15**
- **Why**: Production-grade relational database for Airflow metadata
- **Purpose**: Stores DAG definitions, task execution history, and workflow state
- **Advantages**: Better performance and reliability than SQLite for production workloads

### Event Streaming Layer

**Apache Kafka 7.5.0**
- **Why**: Industry-standard distributed event streaming platform
- **Purpose**: Enables event-driven architecture for decoupled system coordination
- **Key Features**: High throughput, fault tolerance, message persistence
- **Use Case**: Coordinates Airflow workflows with AI agents (LangGraph in Phase 2)

**Zookeeper**
- **Why**: Required for Kafka cluster coordination and metadata management
- **Purpose**: Manages Kafka broker configuration and leader election

### Event Schema & Validation

**Pydantic**
- **Why**: Modern Python data validation library with excellent type safety
- **Purpose**: Validates workflow event schemas, ensures type safety, generates JSON schemas
- **Key Features**: Runtime validation, serialization, automatic documentation

### Development & Testing

**Docker & Docker Compose**
- **Why**: Standard containerization for consistent development environments
- **Purpose**: Isolates services, simplifies setup, enables reproducible deployments
- **Benefits**: One-command environment setup, service orchestration, network isolation

**pytest**
- **Why**: Industry-standard Python testing framework
- **Purpose**: Comprehensive test suite with 176 tests covering all components
- **Coverage**: 97% for TaskFlow DAG code (exceeds 80% requirement)

### Python Libraries

**kafka-python**
- **Why**: Pure Python Kafka client library
- **Purpose**: Producer and consumer implementations for workflow events
- **Features**: Simple API, good error handling, offset management

**Python 3.11+**
- **Why**: Modern Python with improved performance and type hints
- **Purpose**: Base runtime for all components
- **Features**: Type hints, dataclasses, modern async support

## Process Architecture

### Process 1: ETL Workflow Execution (Airflow DAG)

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow Scheduler                        │
│              (Triggers DAG based on schedule)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DAG: example_etl_dag                     │
│              (TaskFlow API with @dag decorator)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────┐            ┌───────────────┐
│  extract()    │            │  transform() │
│  @task        │───────────▶│  @task       │
│  Returns data │  XCom      │  Processes   │
└───────────────┘  Auto      │  data        │
                             └──────┬───────┘
                                    │ XCom
                                    ▼
                          ┌───────────────┐
                          │  validate()   │
                          │  @task.bash   │
                          │  Validates    │
                          └──────┬───────┘
                                 │ XCom
                                 ▼
                          ┌───────────────┐
                          │  load()       │
                          │  @task        │
                          │  Loads data   │
                          └──────┬───────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ publish_completion()    │
                    │ @task                   │
                    │ Publishes to Kafka      │
                    └─────────────────────────┘
```

**Description**: Airflow scheduler triggers DAG execution. Tasks execute sequentially with automatic data passing via XCom. Each task receives data from previous task as function arguments. Final task publishes completion event to Kafka.

---

### Process 2: Event-Driven Workflow Coordination

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow Task Completion                  │
│              (Task or DAG finishes execution)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Creates WorkflowEvent
                       │ (Pydantic validated)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              WorkflowEventProducer                          │
│  - Validates event schema                                   │
│  - Serializes to JSON                                       │
│  - Handles errors gracefully                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Publishes to topic
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Kafka Broker                             │
│              Topic: workflow-events                         │
│  - Stores events persistently                              │
│  - Manages partitions and offsets                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Consumes events
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              WorkflowEventConsumer                          │
│  - Deserializes events                                      │
│  - Validates with Pydantic                                  │
│  - Manages consumer groups                                 │
│  - Handles offset commits                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Processed events
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Event Processing (Phase 2+)                     │
│              (LangGraph workflows, etc.)                    │
└─────────────────────────────────────────────────────────────┘
```

**Description**: Airflow tasks publish workflow events to Kafka upon completion. Events are validated, serialized, and stored in Kafka topics. Consumers process events asynchronously, enabling decoupled coordination between Airflow and AI workflows.

---

### Process 3: Data Passing with XCom (TaskFlow API)

```
┌─────────────────────────────────────────────────────────────┐
│              TaskFlow API Automatic XCom                    │
│         (No manual XCom management required)                 │
└─────────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────┐            ┌───────────────┐
│ Task A        │            │ Task B         │
│ @task         │            │ @task          │
│ def extract() │            │ def transform( │
│     return {  │            │     data: dict │
│       "data": │            │ ) -> dict:     │
│       [1,2,3]│            │     # Process   │
│     }         │            │     return ... │
└───────┬───────┘            └───────┬───────┘
        │                             │
        │ Function call creates       │
        │ automatic dependency        │
        │                             │
        └───────────┬─────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Airflow XCom Store   │
        │  (PostgreSQL)         │
        │  - Auto-serialization  │
        │  - Auto-deserialization│
        │  - Type preservation   │
        └───────────────────────┘
```

**Description**: TaskFlow API automatically manages XCom data passing. Tasks pass data via function arguments - no manual XCom pull/push needed. Airflow handles serialization to PostgreSQL and deserialization when next task receives data. Type hints enable IDE support and validation.

---

### Process 4: Overall System Architecture (Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│              Docker Compose Environment                     │
│              (Local Development)                            │
└─────────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │   Airflow    │ │    Kafka     │
│  (Port 5432) │ │  Webserver   │ │  (Port 9092) │
│              │ │  (Port 8080) │ │              │
│  - DAG defs  │ │              │ │  - Events    │
│  - Task state│ │  - UI        │ │  - Topics    │
│  - XCom data │ │  - Monitoring│ │  - Offsets   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                 │
       │                │                 │
       └────────┬───────┴─────────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │   Airflow Scheduler       │
    │   - Triggers DAGs         │
    │   - Executes tasks        │
    │   - Manages dependencies  │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │   DAG Execution           │
    │   - TaskFlow API          │
    │   - XCom data passing     │
    │   - Event publishing      │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │   Kafka Event Stream       │
    │   - workflow-events topic  │
    │   - Producer/Consumer      │
    │   - Event schema validation│
    └────────────────────────────┘
```

**Description**: Complete Phase 1 architecture showing all services running in Docker Compose. Airflow orchestrates workflows, stores state in PostgreSQL, and publishes events to Kafka. Kafka enables event-driven coordination for future AI workflow integration (Phase 2+).

## Project Structure

```
.
├── .cursor/                  # Cursor AI framework configuration
├── project/                  # Project files
│   ├── dags/                # Airflow DAG definitions
│   ├── logs/                # Airflow execution logs
│   ├── plugins/             # Airflow custom plugins
│   ├── dev/                 # Development files
│   │   ├── tasks/           # Task management
│   │   └── bugs/            # Bug tracking
│   ├── docs/                # Project documentation
│   │   ├── prd.md          # Product Requirements Document
│   │   └── prd_phase*.md   # Phase-specific PRDs
│   └── tests/               # Test suite (modular structure)
│       ├── infrastructure/  # Docker Compose & infrastructure tests
│       ├── airflow/         # Airflow tests (Phase 1.2+)
│       └── kafka/           # Kafka tests (Phase 1.3+)
├── scripts/                 # Utility scripts
│   ├── generate-fernet-key.sh
│   └── test-docker-compose.sh
├── docker-compose.yml       # Docker Compose configuration
├── pytest.ini              # Pytest configuration
├── .env                     # Environment variables (not in git)
└── development_framework_v2a/  # Development framework (excluded from git)
```

## Key Features

- **State-based Orchestration**: Manages agent states across workflow execution
- **AI-Powered Workflows**: Intelligent decision-making in workflow orchestration
- **Trading Operations**: Specialized for trading workflow automation
- **Production Ready**: Designed for scalability and reliability

## Documentation

See `project/docs/prd.md` for the complete Product Requirements Document.

## Development Framework

This project utilizes a self-developed Cursor AI framework to optimize coding speed and maintainability. The framework provides specialized AI personas (Mission Analyst, Mission Planner, Mission Executor, Mission-QA, Mission Challenger, etc.) through slash commands, enabling sequential persona switching and orchestrated multi-agent workflows for complex technical tasks. The framework uses BPMN workflows, quality gates, and state persistence to ensure consistent code quality, comprehensive testing, and efficient project progress while maintaining complete autonomy from the project codebase.

