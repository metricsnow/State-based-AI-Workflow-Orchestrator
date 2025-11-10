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
└── testing-guide-phase1.md     # Testing procedures
```

## Security Requirements

**CRITICAL**: All credentials MUST be stored in `.env` file. This is a MANDATORY security requirement for all phases.

See security sections in each PRD for details.

## Status

- **Phase 1**: In Progress
  - ✅ TASK-001: Docker Compose Environment Setup (Complete)
  - ⏳ TASK-002: Airflow Configuration (Pending)
  - ⏳ TASK-003: Basic DAG Creation (Pending)

## Contributing

When adding new documentation:
1. Follow existing documentation structure
2. Use Markdown format
3. Include code examples where applicable
4. Update this README with new documents
5. Ensure all credentials are documented as using `.env` file

