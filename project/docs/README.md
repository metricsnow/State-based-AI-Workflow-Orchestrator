# Documentation Index

Complete documentation for the AI-Powered Workflow Orchestration project.

## Phase 1 Documentation

### Product Requirements
- **[PRD Phase 1](prd_phase1.md)** - Foundation & Core Orchestration
  - Milestone 1.1: Airflow Setup and Basic DAG
  - Milestone 1.2: TaskFlow API Implementation
  - Milestone 1.3: Kafka Event Streaming Setup

### Setup and Testing
- **[Setup Guide](setup-guide.md)** - Step-by-step environment setup instructions
- **[Testing Guide](testing-guide-phase1.md)** - Comprehensive testing procedures
  - ✅ **Airflow DAG Tests**: 95 tests passing, 97% coverage for TaskFlow DAGs
    - TASK-004: DAG validation (57 tests)
    - TASK-006: XCom data passing (36 tests)
    - TASK-007: Unit tests for TaskFlow DAGs (62 tests, 97% coverage)
  - ✅ **Event Schema Tests**: 26 tests passing (TASK-010)
  - Infrastructure tests, Airflow tests, and testing best practices
- **[TaskFlow API Guide](taskflow-api-guide.md)** - TaskFlow API implementation guide
  - ✅ TASK-005: TaskFlow API migration (Complete)
  - ✅ TASK-006: XCom data passing patterns (Complete)
  - ✅ TASK-007: Unit tests for TaskFlow DAGs (Complete)
- **[Event Schema Guide](event-schema-guide.md)** - Workflow event schema documentation
  - ✅ TASK-010: Event Schema Definition (Complete)
  - Pydantic models, validation, serialization, and JSON schema generation
- **[Kafka Producer Guide](kafka-producer-guide.md)** - Kafka producer usage and configuration
  - ✅ TASK-011: Kafka Producer Implementation (Complete)
  - Producer class, event publishing, error handling, connection management
- **[Kafka Consumer Guide](kafka-consumer-guide.md)** - Kafka consumer usage and configuration
  - ✅ TASK-012: Kafka Consumer Implementation (Complete)
  - Consumer class, event consumption, offset management, error handling
- **[Kafka Setup Guide](kafka-setup-guide.md)** - Kafka infrastructure setup
  - ✅ TASK-009: Kafka Docker Setup (Complete)
  - Zookeeper and Kafka configuration, troubleshooting

### Main PRD
- **[Main PRD](prd.md)** - Complete product requirements document
- **[Phase PRDs](prd_phase*.md)** - Phase-specific requirements (Phases 1-9)

## Quick Links

### Getting Started
1. Read [Setup Guide](setup-guide.md) for environment setup
2. Review [PRD Phase 1](prd_phase1.md) for requirements
3. Check [Testing Guide](testing-guide-phase1.md) for testing procedures

### Development
- **Tasks**: `../dev/tasks/` - Implementation tasks
- **Test Suite**: `../tests/README.md` - Test suite documentation
- **Project README**: `../README.md` - Project overview

## Documentation Structure

```
docs/
├── README.md                    # This file
├── prd.md                       # Main Product Requirements Document
├── prd_phase1.md               # Phase 1 PRD (Foundation)
├── prd_phase2.md               # Phase 2 PRD (AI Workflow Foundation)
├── prd_phase3.md               # Phase 3 PRD (Integration)
├── prd_phase4.md               # Phase 4 PRD (Production Infrastructure)
├── prd_phase5.md               # Phase 5 PRD (Advanced LLM Deployment)
├── prd_phase6.md               # Phase 6 PRD (Advanced AI Features)
├── prd_phase7.md               # Phase 7 PRD (Security & Optimization)
├── prd_phase8.md               # Phase 8 PRD (Developer Experience)
├── prd_phase9.md               # Phase 9 PRD (Enterprise Features)
├── setup-guide.md              # Environment setup guide
├── testing-guide-phase1.md     # Testing procedures
├── taskflow-api-guide.md       # TaskFlow API implementation guide
├── event-schema-guide.md       # Event schema documentation (TASK-010)
├── kafka-producer-guide.md     # Kafka producer usage guide (TASK-011)
├── kafka-consumer-guide.md     # Kafka consumer usage guide (TASK-012)
└── kafka-setup-guide.md        # Kafka infrastructure setup (TASK-009)
```

## Security Requirements

**CRITICAL**: All credentials MUST be stored in `.env` file. This is a MANDATORY security requirement for all phases.

See security sections in each PRD for details.

## Testing Philosophy

**CRITICAL**: All tests run against the **production environment** - **NEVER with placeholders or mocks**.

- Tests use **real services** (PostgreSQL, Kafka, Airflow) from `docker-compose.yml`
- Tests connect to **actual Docker containers** (not mocked)
- Tests validate **real database connections** (PostgreSQL, not SQLite)
- Tests interact with **real Kafka brokers** (not in-memory implementations)
- Tests execute against **real Airflow instances** (not test databases)

**No placeholders. No mocks. Production environment only.**

See [Testing Guide](testing-guide-phase1.md) and [Test Suite README](../tests/README.md) for details.

## Status

- **Phase 1**: In Progress
  - ✅ TASK-001: Docker Compose Environment Setup (Complete)
  - ✅ TASK-002: Airflow Configuration and Initialization (Complete)
  - ✅ TASK-003: Basic DAG Creation with Traditional Operators (Complete)
  - ✅ TASK-004: DAG Validation and Testing (Complete - 57 tests, 100% coverage)
  - ✅ TASK-005: Migrate DAGs to TaskFlow API (Complete - TaskFlow API implemented)
  - ✅ TASK-006: Implement Data Passing with XCom (Complete - 36 tests, all patterns implemented)
  - ✅ TASK-007: Unit Tests for TaskFlow DAGs (Complete - 62 tests, 97% coverage)
  - ✅ TASK-008: Integration Testing for TaskFlow DAGs (Complete - 13 tests)
  - ✅ TASK-009: Kafka Docker Setup (Complete)
  - ✅ TASK-010: Event Schema Definition (Complete - 26 tests, Pydantic models, JSON schema)
  - ✅ TASK-011: Kafka Producer Implementation (Complete - 17 tests, producer class, error handling)
  - ✅ TASK-012: Kafka Consumer Implementation (Complete - 25 tests, consumer class, offset management)

## Contributing

When adding new documentation:
1. Follow existing documentation structure
2. Use Markdown format
3. Include code examples where applicable
4. Update this README with new documents
5. Ensure all credentials are documented as using `.env` file

