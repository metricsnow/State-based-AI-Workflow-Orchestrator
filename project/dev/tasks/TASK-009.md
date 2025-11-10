# TASK-009: Kafka Docker Setup

## Task Information
- **Task ID**: TASK-009
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 2-3 hours
- **Actual Time**: TBD
- **Type**: Feature
- **Dependencies**: TASK-001 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.3

## Task Description
Set up Kafka and Zookeeper services in Docker Compose. Configure Kafka broker with proper networking, health checks, and environment variables. Ensure Kafka is accessible and ready for producer/consumer implementation.

## Problem Statement
Kafka infrastructure is required for event-driven coordination. Kafka needs to be properly configured in Docker Compose with Zookeeper for coordination, proper networking, and health checks.

## Requirements

### Functional Requirements
- [ ] Zookeeper service running
- [ ] Kafka broker service running
- [ ] Kafka accessible on port 9092
- [ ] Zookeeper accessible on port 2181
- [ ] Services have health checks
- [ ] Services can communicate via Docker network
- [ ] Kafka topics can be created

### Technical Requirements
- [ ] Confluent Kafka 7.5.0+ image
- [ ] Confluent Zookeeper 7.5.0+ image
- [ ] Proper Kafka configuration
- [ ] Zookeeper connection configured
- [ ] Health checks implemented
- [ ] Network configuration

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Kafka Docker setup requirements
- [ ] Review Zookeeper configuration
- [ ] Plan Kafka broker configuration
- [ ] Identify required environment variables

### Phase 2: Planning
- [ ] Design Kafka service configuration
- [ ] Plan Zookeeper configuration
- [ ] Design health checks
- [ ] Plan network configuration

### Phase 3: Implementation
- [ ] Add Zookeeper service to docker-compose.yml
- [ ] Add Kafka service to docker-compose.yml
- [ ] Configure Kafka environment variables
- [ ] Configure Zookeeper connection
- [ ] Add health checks
- [ ] Update .env.example

### Phase 4: Testing
- [ ] Start Kafka and Zookeeper services
- [ ] Verify services are healthy
- [ ] Test Kafka connectivity
- [ ] Create test topic
- [ ] Verify service restart

### Phase 5: Documentation
- [ ] Document Kafka configuration
- [ ] Document access URLs and ports
- [ ] Document troubleshooting steps

## Technical Implementation

### Docker Compose Configuration
```yaml
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
    zookeeper:
      condition: service_healthy
  ports:
    - "9092:9092"
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
    KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
  healthcheck:
    test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Test Kafka Connection
```bash
# Test Kafka is running
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Create test topic
docker-compose exec kafka kafka-topics --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

## Testing

### Manual Testing
- [ ] Start services: `docker-compose up -d zookeeper kafka`
- [ ] Verify health: `docker-compose ps`
- [ ] Test Kafka connection
- [ ] Create test topic
- [ ] Verify topic exists
- [ ] Test service restart

### Automated Testing
- [ ] Health check validation
- [ ] Connectivity tests

## Acceptance Criteria
- [ ] Zookeeper service running and healthy
- [ ] Kafka service running and healthy
- [ ] Kafka accessible on port 9092
- [ ] Zookeeper accessible on port 2181
- [ ] Health checks passing
- [ ] Test topic can be created
- [ ] Services can communicate
- [ ] Documentation complete

## Dependencies
- **External**: Docker Compose, Confluent Kafka images
- **Internal**: TASK-001 (Docker Compose setup)

## Risks and Mitigation

### Risk 1: Zookeeper Connection Issues
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Use health checks, proper depends_on, verify network

### Risk 2: Port Conflicts
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Document required ports, check for conflicts

### Risk 3: Kafka Startup Timing
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use health checks, implement retry logic

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete
- [ ] Quality Validation Complete

## Notes
- Kafka requires Zookeeper for coordination
- Use Confluent images for production-ready setup
- Health checks ensure services are ready
- Document Kafka configuration for future reference

