"""
Tests for network connectivity and service communication.
"""
import subprocess
import pytest
import requests
import socket


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.network
class TestPortAccessibility:
    """Test that required ports are accessible."""
    
    def test_airflow_webserver_port(self, required_ports: dict):
        """Test that Airflow webserver port is accessible."""
        port = required_ports["airflow-webserver"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        assert result == 0, f"Port {port} (Airflow webserver) is not accessible"
    
    def test_kafka_port(self, required_ports: dict):
        """Test that Kafka port is accessible."""
        port = required_ports["kafka"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        assert result == 0, f"Port {port} (Kafka) is not accessible"
    
    def test_airflow_ui_accessible(self):
        """Test that Airflow UI is accessible via HTTP."""
        try:
            response = requests.get("http://localhost:8080", timeout=10)
            assert response.status_code in [200, 302, 401], \
                f"Airflow UI returned status code {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Airflow UI is not accessible: {e}")


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.network
class TestServiceCommunication:
    """Test communication between services."""
    
    def test_airflow_to_postgres(self, docker_compose_exec, docker_compose_file: str):
        """Test that Airflow can connect to PostgreSQL."""
        result = docker_compose_exec(
            "airflow-webserver",
            ["ping", "-c", "2", "postgres"]
        )
        # ping may not be available, try alternative
        if result.returncode != 0:
            # Try using nc or telnet
            result = docker_compose_exec(
                "airflow-webserver",
                ["nc", "-z", "postgres", "5432"]
            )
        assert result.returncode == 0, "Airflow cannot reach PostgreSQL"
    
    def test_kafka_to_zookeeper(self, docker_compose_exec, docker_compose_file: str):
        """Test that Kafka can connect to Zookeeper."""
        result = docker_compose_exec(
            "kafka",
            ["ping", "-c", "2", "zookeeper"]
        )
        # ping may not be available, try alternative
        if result.returncode != 0:
            result = docker_compose_exec(
                "kafka",
                ["nc", "-z", "zookeeper", "2181"]
            )
        assert result.returncode == 0, "Kafka cannot reach Zookeeper"


@pytest.mark.docker
@pytest.mark.integration
class TestKafkaConnectivity:
    """Test Kafka-specific connectivity."""
    
    def test_kafka_topic_creation(self, docker_compose_exec, docker_compose_file: str):
        """Test that Kafka topics can be created."""
        # Create a test topic
        result = docker_compose_exec(
            "kafka",
            [
                "kafka-topics",
                "--create",
                "--topic", "test-topic",
                "--bootstrap-server", "localhost:9092",
                "--partitions", "1",
                "--replication-factor", "1",
            ]
        )
        # Topic might already exist, which is OK
        assert result.returncode == 0 or "already exists" in result.stderr.lower(), \
            f"Failed to create Kafka topic: {result.stderr}"
    
    def test_kafka_topic_list(self, docker_compose_exec, docker_compose_file: str):
        """Test that Kafka topics can be listed."""
        result = docker_compose_exec(
            "kafka",
            [
                "kafka-topics",
                "--list",
                "--bootstrap-server", "localhost:9092",
            ]
        )
        assert result.returncode == 0, f"Failed to list Kafka topics: {result.stderr}"

