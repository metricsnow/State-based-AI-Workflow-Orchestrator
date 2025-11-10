# Kafka Setup Guide

## Overview

This guide documents the Kafka and Zookeeper setup for the workflow orchestration system. Kafka is used for event-driven coordination between Airflow and other system components.

## Architecture

The system uses:
- **Zookeeper**: Coordination service for Kafka (required for Kafka < 3.0)
- **Kafka**: Event streaming platform for workflow events
- **Docker Compose**: Container orchestration for local development

## Service Configuration

### Zookeeper

**Container**: `airflow-zookeeper`  
**Image**: `confluentinc/cp-zookeeper:7.5.0`  
**Port**: `2181` (internal only)  
**Health Check**: Network connectivity check on port 2181

**Configuration**:
- `ZOOKEEPER_CLIENT_PORT`: 2181
- `ZOOKEEPER_TICK_TIME`: 2000ms

### Kafka

**Container**: `airflow-kafka`  
**Image**: `confluentinc/cp-kafka:7.5.0`  
**Port**: `9092` (exposed to host)  
**Health Check**: Kafka broker API versions check

**Configuration**:
- `KAFKA_BROKER_ID`: 1
- `KAFKA_ZOOKEEPER_CONNECT`: zookeeper:2181
- `KAFKA_ADVERTISED_LISTENERS`: PLAINTEXT://localhost:9092
- `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`: 1 (single broker)
- `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR`: 1
- `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR`: 1

## Access URLs and Ports

| Service | Port | URL | Access |
|---------|------|-----|--------|
| Kafka | 9092 | `localhost:9092` | External (from host) |
| Zookeeper | 2181 | `zookeeper:2181` | Internal (Docker network only) |

## Starting Services

### Start Kafka and Zookeeper

```bash
docker-compose up -d zookeeper kafka
```

### Verify Services are Healthy

```bash
docker-compose ps zookeeper kafka
```

Both services should show `(healthy)` status.

### Check Service Logs

```bash
# Zookeeper logs
docker-compose logs zookeeper

# Kafka logs
docker-compose logs kafka
```

## Testing Kafka

### Test Kafka Connectivity

```bash
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

This should return a list of supported API versions.

### Create a Test Topic

```bash
docker-compose exec kafka kafka-topics --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

### List Topics

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Describe Topic

```bash
docker-compose exec kafka kafka-topics --describe \
  --topic test-topic \
  --bootstrap-server localhost:9092
```

### Delete Topic

```bash
docker-compose exec kafka kafka-topics --delete \
  --topic test-topic \
  --bootstrap-server localhost:9092
```

## Topic Configuration

### Default Topics

- `workflow-events`: Default topic for workflow events (to be created by producer/consumer)

### Topic Creation

Topics are typically created automatically by producers with the `auto.create.topics.enable` setting, or manually using the `kafka-topics` command.

## Network Configuration

All services are connected via the `airflow-network` Docker network, allowing:
- Kafka to communicate with Zookeeper
- Airflow services to communicate with Kafka
- All services to resolve each other by service name

## Dependencies

Kafka depends on Zookeeper and will wait for Zookeeper to be healthy before starting:

```yaml
depends_on:
  zookeeper:
    condition: service_healthy
```

## Troubleshooting

### Kafka Won't Start

1. **Check Zookeeper is healthy**:
   ```bash
   docker-compose ps zookeeper
   ```

2. **Check Kafka logs**:
   ```bash
   docker-compose logs kafka
   ```

3. **Verify network connectivity**:
   ```bash
   docker-compose exec kafka nc -z zookeeper 2181
   ```

### Port Already in Use

If port 9092 is already in use:

1. **Find process using port**:
   ```bash
   lsof -i :9092
   ```

2. **Stop the conflicting service** or change the port mapping in `docker-compose.yml`

### Kafka Connection Timeout

1. **Verify Kafka is healthy**:
   ```bash
   docker-compose ps kafka
   ```

2. **Test connectivity from host**:
   ```bash
   telnet localhost 9092
   ```

3. **Check firewall settings** (if applicable)

### Topic Creation Fails

1. **Verify Kafka is running**:
   ```bash
   docker-compose ps kafka
   ```

2. **Check Kafka logs for errors**:
   ```bash
   docker-compose logs kafka | tail -50
   ```

3. **Verify replication factor** (must be ≤ number of brokers, which is 1 in this setup)

### Zookeeper Connection Issues

1. **Verify Zookeeper is healthy**:
   ```bash
   docker-compose ps zookeeper
   ```

2. **Test connectivity from Kafka container**:
   ```bash
   docker-compose exec kafka nc -z zookeeper 2181
   ```

3. **Check Zookeeper logs**:
   ```bash
   docker-compose logs zookeeper
   ```

## Health Checks

### Zookeeper Health Check

```bash
docker-compose exec zookeeper nc -z localhost 2181 || exit 1
```

### Kafka Health Check

```bash
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 || exit 1
```

Health checks run automatically every 10 seconds with a 5-second timeout and 5 retries.

## Production Considerations

For production deployments, consider:

1. **Multiple Kafka Brokers**: Increase replication factor and partition count
2. **Kafka without Zookeeper**: Use KRaft mode (Kafka 3.0+)
3. **Security**: Enable SASL/SSL authentication
4. **Monitoring**: Add Kafka metrics and monitoring
5. **Persistence**: Configure proper volume mounts for data retention
6. **Resource Limits**: Set appropriate CPU and memory limits

## Related Documentation

- [Event Schema Guide](event-schema-guide.md) - Event schema definition
- [PRD Phase 1](prd_phase1.md) - Overall architecture and requirements
- [Testing Guide](testing-guide-phase1.md) - Testing procedures

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Platform Documentation](https://docs.confluent.io/)
- [kafka-python Library](https://github.com/dpkp/kafka-python)

