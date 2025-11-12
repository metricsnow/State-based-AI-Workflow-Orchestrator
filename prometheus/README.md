# Prometheus Monitoring Setup

This directory contains Prometheus configuration for monitoring the Airflow-based workflow orchestration system.

## Files

- `prometheus.yml` - Main Prometheus configuration file
- `alerts.yml` - Alerting rules for Prometheus
- `README.md` - This file

## Configuration

### Scrape Targets

Prometheus is configured to scrape metrics from:

1. **Prometheus itself** (`localhost:9090`)
   - Self-monitoring metrics

2. **Airflow Webserver** (`airflow-webserver:8080`)
   - Metrics endpoint: `/admin/metrics`
   - Scrape interval: 30s
   - Includes DAG run states, task states, scheduler metrics

3. **Kafka** (`kafka:9092`)
   - Basic Kafka metrics (JMX exporter can be added for detailed metrics)

### Alerting Rules

Alert rules are defined in `alerts.yml`:

- **AirflowDAGFailed**: Critical alert when a DAG has been in failed state for >5 minutes
- **AirflowTaskFailed**: Warning alert when a task has failed for >5 minutes
- **KafkaConsumerLag**: Warning alert when consumer lag exceeds 1000 messages for >10 minutes
- **PrometheusTargetDown**: Critical alert when a Prometheus scrape target is down for >5 minutes

### Data Retention

- Retention period: 15 days
- Storage path: `/prometheus` (Docker volume)

## Usage

### Start Prometheus

Prometheus is started automatically with Docker Compose:

```bash
docker compose up -d prometheus
```

### Access Prometheus UI

- URL: http://localhost:9090
- Query interface: http://localhost:9090/graph
- Targets status: http://localhost:9090/targets
- Alerts: http://localhost:9090/alerts

### Common Queries

```promql
# Check if Airflow is up
up{job="airflow"}

# DAG run states
airflow_dag_run_state

# Task instance states
airflow_task_instance_state

# Failed DAG runs
airflow_dag_run_state{state="failed"}

# All targets status
up
```

## Troubleshooting

### Prometheus not scraping targets

1. Check target status: http://localhost:9090/targets
2. Verify network connectivity between containers
3. Check service names match docker-compose.yml
4. Verify metrics endpoints are accessible

### Alerts not firing

1. Check alert rules: http://localhost:9090/alerts
2. Verify alert expressions are correct
3. Check alert thresholds are appropriate
4. Verify metrics exist for alert expressions

### Configuration changes

After modifying `prometheus.yml` or `alerts.yml`:

1. Restart Prometheus: `docker compose restart prometheus`
2. Or reload configuration: `curl -X POST http://localhost:9090/-/reload` (if enabled)

## Notes

- Airflow 2.8.4 has built-in Prometheus metrics at `/admin/metrics`
- No additional configuration needed for Airflow metrics exposure
- Kafka metrics may require JMX exporter for detailed metrics
- Alertmanager can be added later for alert routing and notifications

