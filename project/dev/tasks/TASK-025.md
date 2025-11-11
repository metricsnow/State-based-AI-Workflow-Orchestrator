# TASK-025: Add Ollama Service to Docker Compose

## Task Information
- **Task ID**: TASK-025
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 1-2 hours
- **Actual Time**: TBD
- **Type**: Infrastructure
- **Dependencies**: None
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Add Ollama service to Docker Compose configuration to enable local LLM deployment in containerized environment. Configure health checks, networking, and volume persistence for model storage.

## Problem Statement
Ollama needs to be available as a Docker service for consistent development and deployment environments. The PRD shows optional Docker integration, but it should be mandatory for Phase 3 to ensure consistent environments.

## Requirements

### Functional Requirements
- [ ] Ollama service added to docker-compose.yml
- [ ] Service configured with proper ports (11434)
- [ ] Volume persistence for model storage
- [ ] Health check configured
- [ ] Network integration with airflow-network
- [ ] Environment variables configured
- [ ] Service accessible from other containers

### Technical Requirements
- [ ] Docker Compose service definition
- [ ] Health check using Ollama API
- [ ] Volume mount for `/root/.ollama`
- [ ] Network configuration (airflow-network)
- [ ] Environment variable for OLLAMA_HOST
- [ ] Service dependency management (if needed)

## Implementation Plan

### Phase 1: Analysis
- [ ] Review current docker-compose.yml structure
- [ ] Review Ollama Docker image requirements
- [ ] Plan service configuration
- [ ] Identify network requirements

### Phase 2: Planning
- [ ] Design Ollama service configuration
- [ ] Plan health check implementation
- [ ] Plan volume configuration
- [ ] Plan network integration

### Phase 3: Implementation
- [ ] Add Ollama service to docker-compose.yml
- [ ] Configure ports (11434:11434)
- [ ] Configure volume for model persistence
- [ ] Add health check configuration
- [ ] Configure network (airflow-network)
- [ ] Set environment variables (OLLAMA_HOST=0.0.0.0)
- [ ] Add volume definition to volumes section

### Phase 4: Testing
- [ ] Start Docker Compose services
- [ ] Verify Ollama service starts successfully
- [ ] Verify health check passes
- [ ] Verify service accessible on port 11434
- [ ] Verify network connectivity from other services
- [ ] Test model download via Ollama API

### Phase 5: Documentation
- [ ] Document Ollama service configuration
- [ ] Document health check behavior
- [ ] Document volume persistence
- [ ] Document network access patterns

## Technical Implementation

### Docker Compose Service Configuration
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: airflow-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - airflow-network
    restart: unless-stopped

volumes:
  ollama_data:
    driver: local
```

### Integration Points
- **Network**: `airflow-network` (shared with Airflow, Kafka)
- **Port**: `11434` (Ollama API port)
- **Volume**: `ollama_data` (persists models across restarts)
- **Health Check**: Uses `/api/tags` endpoint to verify service

## Testing

### Manual Testing
- [ ] Start services: `docker-compose up -d ollama`
- [ ] Verify service status: `docker-compose ps ollama`
- [ ] Check health: `curl http://localhost:11434/api/tags`
- [ ] Test from Airflow container: `docker exec airflow-webserver curl http://ollama:11434/api/tags`
- [ ] Verify volume persistence: `docker volume inspect project2_ollama_data`
- [ ] Test model pull: `docker exec airflow-ollama ollama pull llama2`

### Automated Testing
- [ ] Docker Compose service validation
- [ ] Health check validation
- [ ] Network connectivity tests
- [ ] Volume mount verification

## Acceptance Criteria
- [ ] Ollama service added to docker-compose.yml
- [ ] Service starts successfully
- [ ] Health check passes
- [ ] Service accessible on port 11434
- [ ] Network connectivity verified
- [ ] Volume persistence working
- [ ] Service accessible from other containers
- [ ] Documentation complete

## Dependencies
- **External**: Docker, Docker Compose
- **Internal**: None (foundation task)

## Risks and Mitigation

### Risk 1: Health Check Failures
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Use appropriate start_period, verify curl available in image, test health check endpoint

### Risk 2: Network Connectivity Issues
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Verify network configuration, test connectivity from other services, check firewall rules

### Risk 3: Volume Persistence Issues
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Verify volume mount path, test volume creation, verify data persistence across restarts

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- Use `ollama/ollama:latest` image (official image)
- Configure `OLLAMA_HOST=0.0.0.0` to allow external connections
- Health check uses `/api/tags` endpoint (lightweight check)
- Volume persists models to avoid re-downloading
- Network integration enables access from Airflow and LangGraph services

