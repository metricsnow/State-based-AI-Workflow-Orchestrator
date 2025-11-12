# Monitoring Setup Guide - Prometheus & Grafana

**Status**: ✅ Complete (TASK-039)  
**Parent PRD**: `prd_phase4.md` - Milestone 1.8  
**Implementation Date**: 2025-01-27

## Overview

This guide documents the Prometheus and Grafana monitoring setup for the AI-Powered Workflow Orchestration system. The monitoring infrastructure provides observability for Airflow, Kafka, and other services.

## Architecture

```
┌──────────────┐
│  Prometheus  │ ← Scrapes metrics from services
│  Port 9090   │
└──────┬───────┘
       │
┌──────▼───────┐
│   Grafana    │ ← Visualizes metrics from Prometheus
│  Port 3000   │
└──────────────┘
```

## Services Monitored

1. **Prometheus** (self-monitoring)
2. **Airflow Webserver** (`/admin/metrics` endpoint)
3. **Kafka** (basic metrics)
4. **PostgreSQL** (via exporter - optional)

## Quick Start

### Access Points

- **Prometheus UI**: http://localhost:9090
- **Grafana UI**: http://localhost:3000
  - Default username: `admin`
  - Default password: `admin` (change via `.env` file)

### Start Services

```bash
# Start Prometheus and Grafana
docker compose up -d prometheus grafana

# Check status
docker compose ps prometheus grafana

# View logs
docker compose logs -f prometheus grafana
```

## Configuration

### Prometheus Configuration

**File**: `prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'local'
    environment: 'development'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'airflow'
    metrics_path: '/admin/metrics'
    static_configs:
      - targets: ['airflow-webserver:8080']
        labels:
          service: 'airflow'
  
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9092']
        labels:
          service: 'kafka'
```

### Alerting Rules

**File**: `prometheus/alerts.yml`

Configured alerts:
- **AirflowDAGFailed**: Critical alert when DAG fails for >5 minutes
- **AirflowTaskFailed**: Warning alert when task fails for >5 minutes
- **KafkaConsumerLag**: Warning alert when consumer lag >1000 messages
- **PrometheusTargetDown**: Critical alert when scrape target is down

### Grafana Configuration

**Datasource**: `grafana/datasources/prometheus.yml`
- Auto-provisioned Prometheus datasource
- URL: `http://prometheus:9090`
- Default datasource: Yes

**Dashboards**: `grafana/dashboards/`
- Auto-provisioned from JSON files
- Airflow Overview dashboard included

## Docker Compose Integration

Services are integrated in `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=15d'

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
```

## Airflow Metrics

Airflow 2.8.4 exposes Prometheus metrics natively at `/admin/metrics`.

**Configuration**: Enabled via environment variable:
```yaml
- AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
```

**Available Metrics**:
- DAG run states
- Task instance states
- Scheduler metrics
- Webserver metrics

## Common Prometheus Queries

```promql
# Check if Airflow is up
up{job="airflow"}

# DAG run states
airflow_dag_run_state

# Failed DAG runs
airflow_dag_run_state{state="failed"}

# Task instance states
airflow_task_instance_state

# All targets status
up
```

## Grafana Dashboards

### Airflow Overview Dashboard

**Location**: `grafana/dashboards/airflow-overview.json`

**Panels**:
- Airflow Service Status (timeseries)
- Airflow Health (gauge)
- DAG Run States (timeseries)

**Access**: http://localhost:3000 → Dashboards → Airflow Overview

## Environment Variables

Configure Grafana credentials via `.env` file:

```bash
# Grafana Admin Credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password_here
```

**CRITICAL**: Always use `.env` file for credentials. Never hardcode passwords.

## Data Retention

- **Prometheus**: 15 days (configurable)
- **Grafana**: Persistent storage via Docker volume

## Troubleshooting

### Prometheus Not Scraping Targets

1. Check target status: http://localhost:9090/targets
2. Verify network connectivity:
   ```bash
   docker compose exec prometheus ping airflow-webserver
   ```
3. Check service names match docker-compose.yml
4. Verify metrics endpoints are accessible

### Grafana Not Connecting to Prometheus

1. Verify Prometheus is running: `docker compose ps prometheus`
2. Check datasource configuration in Grafana UI
3. Test connection: Configuration → Data Sources → Prometheus → Test

### Dashboards Not Appearing

1. Check dashboard provisioning: Configuration → Provisioning → Dashboards
2. Verify JSON syntax is valid
3. Check Grafana logs: `docker compose logs grafana`
4. Restart Grafana: `docker compose restart grafana`

### Metrics Not Visible

1. Verify Airflow metrics endpoint: http://localhost:8080/admin/metrics
2. Check Prometheus scrape configuration
3. Verify scrape interval is appropriate (15s default)
4. Check Prometheus targets page for errors

## File Structure

```
prometheus/
├── prometheus.yml      # Main Prometheus configuration
├── alerts.yml          # Alerting rules
└── README.md           # Prometheus documentation

grafana/
├── datasources/
│   └── prometheus.yml  # Prometheus datasource configuration
├── dashboards/
│   ├── dashboards.yml  # Dashboard provisioning configuration
│   └── airflow-overview.json  # Airflow dashboard
└── README.md           # Grafana documentation
```

## Testing

### Manual Testing

1. **Verify Prometheus Targets**:
   - Access: http://localhost:9090/targets
   - All targets should show as "UP"

2. **Verify Grafana Dashboards**:
   - Access: http://localhost:3000
   - Login with admin credentials
   - Navigate to Dashboards → Airflow Overview
   - Verify metrics are displayed

3. **Test Alert Rules**:
   - Access: http://localhost:9090/alerts
   - Verify alert rules are loaded
   - Check alert expressions are valid

### Automated Testing

Integration tests verify:
- Service health checks
- Network connectivity
- Port accessibility

Run tests:
```bash
pytest project/tests/infrastructure/test_networking.py -v
pytest project/tests/infrastructure/test_services.py::TestServiceHealth -v
```

## Next Steps

1. **Add More Dashboards**: Create additional dashboards for Kafka, system metrics
2. **Configure Alertmanager**: Set up alert routing and notifications
3. **Add Custom Metrics**: Instrument application code with Prometheus client
4. **Expand Monitoring**: Add PostgreSQL exporter, Kafka JMX exporter

## References

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Airflow Metrics**: https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/metrics.html
- **Task Documentation**: `../dev/tasks/TASK-039.md`
- **PRD**: `prd_phase4.md` - Milestone 1.8

## Status

✅ **Complete** - All acceptance criteria met:
- [x] Prometheus collecting metrics from all services
- [x] Grafana dashboard created with key metrics
- [x] Airflow metrics exposed and collected
- [x] Basic alerting rules configured
- [x] Metrics visible in Grafana
- [x] All services integrated in Docker Compose
- [x] Data persistence working
- [x] Documentation complete

