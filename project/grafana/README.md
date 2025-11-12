# Grafana Monitoring Dashboards

This directory contains Grafana configuration for visualizing metrics from Prometheus.

## Directory Structure

```
grafana/
├── datasources/
│   └── prometheus.yml      # Prometheus datasource configuration
├── dashboards/
│   ├── dashboards.yml      # Dashboard provisioning configuration
│   └── airflow-overview.json  # Airflow overview dashboard
└── README.md               # This file
```

## Configuration

### Datasource

Prometheus datasource is automatically provisioned from `datasources/prometheus.yml`:
- Name: Prometheus
- Type: prometheus
- URL: http://prometheus:9090
- Default: Yes

### Dashboards

Dashboards are automatically provisioned from `dashboards/` directory:
- Dashboard provider: File-based
- Auto-discovery: Enabled
- Editable: Yes

## Usage

### Start Grafana

Grafana is started automatically with Docker Compose:

```bash
docker compose up -d grafana
```

### Access Grafana UI

- URL: http://localhost:3002
- Default username: `admin`
- Default password: `admin` (change in production via `.env` file)
- **Note**: Port changed to 3002 to avoid conflict with Open WebUI (port 3000) and other services (port 3001)

### Available Dashboards

1. **Airflow Overview** (`airflow-overview`)
   - Airflow service status
   - DAG run states
   - Task execution metrics

### Creating New Dashboards

1. Create dashboard in Grafana UI
2. Export as JSON
3. Save to `dashboards/` directory
4. Restart Grafana or wait for auto-provisioning

## Environment Variables

Configure Grafana via environment variables in `.env`:

```bash
# Grafana Admin Credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password_here
```

**CRITICAL**: Always use `.env` file for credentials. Never hardcode passwords.

## Troubleshooting

### Datasource not connecting

1. Verify Prometheus is running: `docker compose ps prometheus`
2. Check network connectivity: `docker compose exec grafana ping prometheus`
3. Verify datasource configuration in Grafana UI: Configuration → Data Sources

### Dashboards not appearing

1. Check dashboard provisioning: Configuration → Provisioning → Dashboards
2. Verify JSON syntax is valid
3. Check Grafana logs: `docker compose logs grafana`
4. Restart Grafana: `docker compose restart grafana`

### Authentication issues

1. Verify environment variables are set correctly
2. Check `.env` file exists and contains credentials
3. Reset admin password if needed (see Grafana documentation)

## Notes

- Dashboards are automatically provisioned on startup
- Changes to dashboard JSON files require Grafana restart
- Datasource configuration is read-only (managed via files)
- All credentials must be in `.env` file (security requirement)

