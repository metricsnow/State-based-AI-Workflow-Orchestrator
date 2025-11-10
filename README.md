# State-based AI Workflow Orchestrator

**AI-Powered Workflow Orchestration for Trading Operations**

## Overview

An AI-powered workflow orchestration system that combines traditional data pipeline orchestration (Airflow) with modern AI capabilities (LangGraph) to create intelligent, automated trading operations workflows.

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

## Current Status

### Phase 1: Foundation & Core Orchestration

- ✅ **TASK-001**: Docker Compose Environment Setup (Completed 2025-11-10)
  - Infrastructure services (PostgreSQL, Zookeeper, Kafka) operational
  - Docker Compose configuration validated (11/11 tests passing)
  - Environment setup complete (.env, .env.example created)
  - Test suite created and passing
  
- ⏳ **TASK-002**: Airflow Configuration and Initialization (Next)
  - Database initialization required before Airflow services can start

## Documentation

See `project/docs/prd.md` for the complete Product Requirements Document.

## Development Framework

This project uses the Development Framework v2 for AI-assisted development. The framework configuration is in `.cursor/` directory.

## License

[To be determined]

