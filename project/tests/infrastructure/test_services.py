"""
Tests for Docker Compose service health and functionality.
"""
import subprocess
import time
import pytest
import requests


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.slow
class TestServiceStartup:
    """Test that services start successfully."""
    
    def test_services_start(self, docker_compose_file: str, docker_compose_services: list):
        """Test that all services can start."""
        # Start services
        result = subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "up", "-d"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Failed to start services: {result.stderr}"
    
    def test_services_running(self, docker_compose_file: str, docker_compose_services: list):
        """Test that all services are running."""
        result = subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "ps"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        for service in docker_compose_services:
            assert service in result.stdout, f"Service '{service}' not found in docker-compose ps"
            # Check that service is running (not exited)
            assert "Exited" not in result.stdout or f"{service}" not in result.stdout.split("Exited")[0], \
                f"Service '{service}' has exited"


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.health
class TestServiceHealth:
    """Test service health checks."""
    
    def test_postgres_health(self, docker_compose_exec, docker_compose_file: str):
        """Test PostgreSQL health check."""
        result = docker_compose_exec("postgres", ["pg_isready", "-U", "airflow"])
        assert result.returncode == 0, f"PostgreSQL health check failed: {result.stderr}"
        assert "accepting connections" in result.stdout.lower()
    
    def test_zookeeper_health(self, docker_compose_exec, docker_compose_file: str):
        """Test Zookeeper health check."""
        result = docker_compose_exec("zookeeper", ["nc", "-z", "localhost", "2181"])
        # nc returns 0 on success, but may not have stdout
        assert result.returncode == 0, f"Zookeeper health check failed"
    
    def test_kafka_health(self, docker_compose_exec, docker_compose_file: str):
        """Test Kafka health check."""
        # Wait a bit for Kafka to be ready
        time.sleep(5)
        result = docker_compose_exec(
            "kafka",
            ["kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
        )
        assert result.returncode == 0, f"Kafka health check failed: {result.stderr}"
    
    def test_airflow_webserver_health(self, docker_compose_file: str):
        """Test Airflow webserver health check."""
        # Wait for webserver to be ready
        max_retries = 12
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(5)
        
        pytest.fail("Airflow webserver health check failed - service not responding")


@pytest.mark.docker
@pytest.mark.integration
class TestServiceLogs:
    """Test service logs for errors."""
    
    def test_postgres_no_critical_errors(self, docker_compose_file: str):
        """Test that PostgreSQL has no critical errors in logs."""
        result = subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "logs", "postgres"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Check for common error patterns
        error_patterns = ["FATAL", "ERROR", "panic"]
        for pattern in error_patterns:
            assert pattern not in result.stdout.upper(), \
                f"PostgreSQL logs contain {pattern} errors"
    
    def test_airflow_webserver_no_critical_errors(self, docker_compose_file: str):
        """Test that Airflow webserver has no critical errors in logs."""
        result = subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "logs", "airflow-webserver"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Airflow may have warnings, but should not have fatal errors
        fatal_patterns = ["FATAL", "Traceback"]
        for pattern in fatal_patterns:
            # Allow some time for startup
            if "Traceback" in result.stdout:
                # Check if it's a recent error (not from old runs)
                lines = result.stdout.split("\n")
                traceback_lines = [i for i, line in enumerate(lines) if "Traceback" in line]
                if traceback_lines:
                    # If traceback is in last 50 lines, it's likely a current error
                    if traceback_lines[-1] > len(lines) - 50:
                        pytest.fail("Airflow webserver has recent traceback in logs")

