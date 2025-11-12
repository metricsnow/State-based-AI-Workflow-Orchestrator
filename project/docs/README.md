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
- **[Airflow-Kafka Integration Guide](airflow-kafka-integration-guide.md)** - Airflow-Kafka integration
  - ✅ TASK-013: Airflow-Kafka Integration (Complete)
  - Reusable utilities, TaskFlow API integration, event publishing

## Phase 4 Documentation

### Production Infrastructure
- **[Monitoring Setup Guide](monitoring-setup-guide.md)** - Prometheus and Grafana monitoring
  - ✅ TASK-039: Monitoring Setup (Prometheus/Grafana) (Complete)
  - Prometheus configuration and metric collection
  - Grafana dashboards and visualization
  - Alerting rules configuration
  - Airflow metrics exposure
  - Docker Compose integration
  - Access URLs and troubleshooting
  - **Status**: All services operational, metrics collecting, dashboards functional

## Phase 3 Documentation

### LLM Integration
- **[LangChain LLM Integration Guide](langchain-ollama-integration-guide.md)** - Unified LLM integration (Ollama and OpenAI)
  - ✅ TASK-026: LangChain-Ollama Package Integration (Complete)
  - ✅ TASK-033: Set Up Ollama with LangChain Integration (Complete)
  - ✅ TASK-038: Unified LLM Factory with Model Toggle (Complete)
  - Package installation, correct import patterns, basic usage
  - Unified factory pattern supporting Ollama and OpenAI (`langchain_ollama_integration`)
  - Environment variable configuration support
  - Default to cheapest OpenAI model (`gpt-4o-mini`) for cost optimization
  - Automatic fallback mechanism (OpenAI → Ollama)
  - LangChain and LangGraph integration examples
  - Compatibility verification, troubleshooting
  - 20 comprehensive production tests, all passing
  - **CRITICAL**: All tests use production conditions - no mocks, no placeholders
  - **COST PROTECTION**: OpenAI tests disabled by default (set `ENABLE_OPENAI_TESTS=true` to enable)
- **[Ollama Model Management Guide](ollama-model-management-guide.md)** - Ollama model download and validation
  - ✅ TASK-036: Model Download and Validation (Complete)
  - Model download script, validation script, Docker setup script
  - Model selection recommendations, troubleshooting
  - Integration with LangChain-Ollama integration
- **[LangGraph LLM Nodes Guide](langgraph-llm-nodes-guide.md)** - LLM nodes for LangGraph workflows
  - ✅ TASK-034: Create LangGraph Node with Ollama LLM (Complete)
  - ✅ TASK-038: Unified LLM Factory Integration (Complete)
  - Factory pattern for creating configurable LLM nodes
  - Unified LLM factory supporting Ollama and OpenAI providers
  - Automatic provider selection via environment variables
  - Prompt templating support with LangChain PromptTemplate
  - Integration with MultiAgentState for multi-agent workflows
  - Error handling and graceful failure recovery
  - 12 comprehensive production tests, all passing
  - Runtime: < 1 second for all tests
  - **CRITICAL**: All tests use production conditions - no mocks, no placeholders

### LangGraph-Kafka Integration
- **[LangGraph Kafka Integration Guide](langgraph-kafka-integration-guide.md)** - Async Kafka consumer for LangGraph workflows
  - ✅ TASK-027: Async LangGraph Kafka Consumer Service (Complete)
    - Async Kafka consumer implementation using aiokafka
    - Non-blocking event processing with concurrent workflow execution
    - Error handling and graceful shutdown
    - Configuration management and service entry point
  - ✅ TASK-028: Result Return Mechanism (Complete)
    - Result producer for publishing workflow results
    - Result polling mechanism for Airflow tasks
    - Correlation ID matching for request/response pairing
  - ✅ TASK-029: LangGraph Workflow Integration (Complete)
    - Event-to-state conversion for LangGraph workflows
    - Complete workflow execution integration
    - Result publishing integration
    - Checkpointing preserved (uses event_id as thread_id)
  - ✅ TASK-030: Airflow Task for Triggering LangGraph Workflows (Complete)
    - Reusable `@task` decorated function for triggering workflows
    - Publishes workflow trigger events to Kafka
    - Polls for workflow results with timeout
    - Automatic DAG context extraction
    - Error handling for timeouts and failures
    - Returns workflow result data to downstream tasks
    - Example DAG demonstrating complete integration pattern
  - ✅ TASK-031: Error Handling and Retry Mechanisms (Complete)
    - Retry utility with exponential backoff and jitter
    - Dead letter queue for failed events
    - Error classification (transient vs permanent errors)
    - Automatic retry for transient errors (ConnectionError, TimeoutError, etc.)
    - DLQ publishing for events that fail after max retries
    - Error result publishing to result topic
    - Comprehensive error handling integration in consumer
    - 27 comprehensive production tests (13 retry tests + 8 DLQ tests + 6 integration tests), all passing
  - ✅ **TASK-032: End-to-End Integration Testing (Complete)**
    - Complete pipeline integration tests (Airflow → Kafka → LangGraph → Result)
    - All 7 Milestone 1.6 acceptance criteria validated
    - 14 comprehensive integration tests, all passing
    - Error handling, timeout, retry, and DLQ scenarios tested
    - Execution time: ~31 seconds (under 1 minute requirement)
  - 76+ comprehensive production tests, all passing
  - **CRITICAL**: All tests use production conditions - no mocks, no placeholders

## Phase 2 Documentation

### AI Workflow Foundation
- **[LangGraph State Guide](langgraph-state-guide.md)** - LangGraph state definitions and reducers
  - ✅ TASK-015: State Definition and Reducers Implementation (Complete)
  - ✅ TASK-020: Multi-Agent State Structure Design (Complete)
  - State schemas (WorkflowState, SimpleState, MultiAgentState), reducers (merge_dicts, last_value, add_messages, merge_agent_results)
  - State validation, usage examples, best practices
  - 45 comprehensive tests, all passing
- **[LangGraph Agent Nodes Guide](langgraph-agent-nodes-guide.md)** - Specialized agent nodes for multi-agent workflows
  - ✅ TASK-021: Specialized Agent Nodes Implementation (Complete)
  - data_agent and analysis_agent nodes with error handling versions
  - State update patterns, result formats, integration examples
  - 16 comprehensive tests, all passing with production conditions
- **[LangGraph LLM Nodes Guide](langgraph-llm-nodes-guide.md)** - LLM nodes for AI-powered workflows
  - ✅ TASK-034: Create LangGraph Node with Ollama LLM (Complete)
  - create_llm_node factory function for configurable LLM nodes
  - llm_analysis_node for multi-agent workflow integration
  - Prompt templating, error handling, state management
  - 12 comprehensive production tests, all passing
- **[LangGraph Orchestrator Guide](langgraph-orchestrator-guide.md)** - Orchestrator agent for multi-agent coordination
  - ✅ TASK-022: Orchestrator Agent Node Implementation (Complete)
  - orchestrator_agent and route_to_agent functions with error handling
  - Orchestrator-worker pattern, workflow coordination, completion detection
  - 21 comprehensive tests, all passing with production conditions
- **[LangGraph Multi-Agent Workflow Guide](langgraph-multi-agent-workflow-guide.md)** - Complete multi-agent workflow with StateGraph
  - ✅ TASK-023: Multi-Agent StateGraph Configuration (Complete)
  - StateGraph configuration with orchestrator, data_agent, and analysis_agent nodes
  - Conditional routing, checkpointing, and orchestrator-worker pattern
  - 19 comprehensive tests, all passing with production conditions
- **[LangGraph Multi-Agent Integration Testing](project/tests/langgraph/README.md#test_multi_agent_integrationpy--complete)** - Comprehensive integration tests for multi-agent workflow
  - ✅ TASK-024: Multi-Agent Collaboration Testing (Complete)
  - All 8 Milestone 1.5 acceptance criteria validated
  - Complete workflow execution, agent collaboration, state management
  - Conditional routing, checkpointing, error handling
  - 17 comprehensive integration tests, all passing
  - 100% code coverage for `multi_agent_workflow.py`
  - **CRITICAL**: All tests use production conditions - no mocks, no placeholders
- **[LangGraph Conditional Routing Guide](langgraph-conditional-routing-guide.md)** - Conditional routing in LangGraph workflows
  - ✅ TASK-017: Conditional Routing Implementation (Complete)
  - Routing functions, conditional edges, dynamic workflow execution
  - Multiple routing patterns, error handling, best practices
  - 25 comprehensive tests, all passing
- **[LangGraph Checkpointing Guide](langgraph-checkpointing-guide.md)** - Checkpointing with InMemorySaver
  - ✅ TASK-018: Checkpointing Configuration and Testing (Complete)
  - InMemorySaver checkpointer, state persistence, workflow resumption
  - Thread ID management, checkpoint save/load, state merging
  - 22 comprehensive tests, all passing
- **[LangGraph Integration Testing](project/tests/langgraph/README.md)** - Complete stateful workflow integration tests
  - ✅ TASK-019: Stateful Workflow Integration Tests (Complete)
  - End-to-end workflow execution, state persistence, conditional routing integration
  - Checkpointing integration, workflow resumption, error handling
  - All Milestone 1.4 acceptance criteria validated
  - 30 comprehensive integration tests, all passing
  - 100% code coverage for all LangGraph workflow modules
  - **CRITICAL**: All tests use production conditions - no mocks, no placeholders

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
├── kafka-setup-guide.md        # Kafka infrastructure setup (TASK-009)
├── langgraph-state-guide.md    # LangGraph state definitions (TASK-015)
├── langgraph-conditional-routing-guide.md  # Conditional routing (TASK-017)
├── langgraph-checkpointing-guide.md  # Checkpointing (TASK-018)
├── langgraph-agent-nodes-guide.md  # Agent nodes (TASK-021)
├── langgraph-llm-nodes-guide.md  # LLM nodes (TASK-034, TASK-038)
├── unified-llm-factory-guide.md  # Unified LLM factory (TASK-038)
├── langgraph-orchestrator-guide.md  # Orchestrator agent (TASK-022)
├── langgraph-multi-agent-workflow-guide.md  # Multi-agent workflow (TASK-023)
├── langchain-ollama-integration-guide.md  # LangChain-Ollama integration (TASK-026)
├── langgraph-kafka-integration-guide.md  # LangGraph Kafka integration (TASK-027)
└── monitoring-setup-guide.md  # Prometheus/Grafana monitoring (TASK-039)
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

- **Phase 4**: 🚧 **IN PROGRESS** - Milestone 1.8 (Monitoring) ✅ Complete
  - ✅ TASK-039: Monitoring Setup (Prometheus/Grafana) (Complete)
  - Milestone 1.9 (Docker Containerization) - Pending
  - Milestone 1.10 (FastAPI Orchestration API) - Pending

- **Phase 1**: ✅ **COMPLETE** - All milestones and deliverables completed
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
  - ✅ TASK-013: Airflow-Kafka Integration (Complete - 15 integration tests, reusable utilities)

**Phase 1 Summary**:
- **Total Tests**: 176 tests (all passing)
- **Test Coverage**: 97% for TaskFlow DAG code (exceeds 80% requirement)
- **DAGs**: 2 DAGs using TaskFlow API (`example_etl_dag.py`, `xcom_data_passing_dag.py`)
- **Documentation**: 10+ comprehensive guides
- **Status**: Production-ready for Phase 1 scope

**Phase 2 Progress**:
- ✅ TASK-014: LangGraph Development Environment Setup (Complete - 5 tests)
- ✅ TASK-015: State Definition and Reducers Implementation (Complete - 26 tests)
- ✅ TASK-016: Basic StateGraph with Nodes Implementation (Complete - 18 tests)
- ✅ TASK-017: Conditional Routing Implementation (Complete - 15 tests)
- ✅ TASK-018: Checkpointing Configuration and Testing (Complete - 22 tests)
- ✅ TASK-019: Stateful Workflow Integration Tests (Complete - 30 tests)
- ✅ TASK-020: Multi-Agent State Structure Design (Complete - included in state tests)
- ✅ TASK-021: Specialized Agent Nodes Implementation (Complete - 16 tests)
- ✅ TASK-022: Orchestrator Agent Node Implementation (Complete - 21 tests)
- ✅ TASK-023: Multi-Agent StateGraph Configuration (Complete - 19 tests)
- ✅ TASK-024: Multi-Agent Collaboration Testing (Complete - 17 tests)
- **Total Tests**: 217 LangGraph tests (all passing)
- **Status**: Milestone 1.5 complete - All multi-agent workflow components tested and validated

**Phase 3 Progress**:
- ✅ TASK-025: Ollama Service Docker Integration (Complete)
- ✅ TASK-026: LangChain-Ollama Package Integration (Complete - 13 tests)
- ✅ TASK-033: Set Up Ollama with LangChain Integration (Complete - 8 tests)
- ✅ TASK-034: Create LangGraph Node with Ollama LLM (Complete - 12 tests)
- ✅ TASK-027: Async LangGraph Kafka Consumer Service (Complete - 22 tests)
- ✅ TASK-028: Result Return Mechanism (Complete - 7 tests)
- ✅ TASK-029: LangGraph Workflow Integration (Complete - 7 tests)
- ✅ TASK-030: Airflow-LangGraph Integration (Complete)
- ✅ TASK-031: Error Handling and Retry Mechanisms (Complete - 27 tests)
- ✅ TASK-032: End-to-End Integration Testing (Complete - 14 tests)
- **Total Tests**: 110+ Phase 3 tests (all passing)
- **Status**: Milestone 1.7 in progress - LLM integration components tested and validated

**Completed**: 
- TASK-022 (Orchestrator Agent Node Implementation) - orchestrator_agent and route_to_agent with error handling, 21 tests passing
- TASK-023 (Multi-Agent StateGraph Configuration) - Complete StateGraph with orchestrator-worker pattern, checkpointing, 19 tests passing
- TASK-024 (Multi-Agent Collaboration Testing) - Comprehensive integration tests validating all Milestone 1.5 acceptance criteria, 17 tests passing, 100% coverage for multi_agent_workflow.py

## Contributing

When adding new documentation:
1. Follow existing documentation structure
2. Use Markdown format
3. Include code examples where applicable
4. Update this README with new documents
5. Ensure all credentials are documented as using `.env` file

