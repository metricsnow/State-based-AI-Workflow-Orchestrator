"""
Pytest fixtures for Docker Compose environment testing.
"""
import os
import subprocess
import time
import pytest
from typing import Generator, Dict, List


@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Return the path to docker-compose.yml."""
    # Navigate from project/tests/infrastructure/ to root/docker-compose.yml
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docker-compose.yml")


@pytest.fixture(scope="session")
def env_file() -> str:
    """Return the path to .env file."""
    # Navigate from project/tests/infrastructure/ to root/.env
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")


@pytest.fixture(scope="session")
def docker_compose_services() -> List[str]:
    """Return list of required services."""
    return [
        "postgres",
        "zookeeper",
        "kafka",
        "airflow-webserver",
        "airflow-scheduler",
    ]


@pytest.fixture(scope="session")
def docker_compose_up(docker_compose_file: str, env_file: str) -> Generator[None, None, None]:
    """
    Start Docker Compose services before tests and stop after.
    
    This fixture ensures services are running for integration tests.
    """
    # Check if .env file exists
    if not os.path.exists(env_file):
        pytest.skip(f".env file not found at {env_file}. Please create it first.")
    
    # Start services
    print("\n[SETUP] Starting Docker Compose services...")
    subprocess.run(
        ["docker-compose", "-f", docker_compose_file, "up", "-d"],
        check=False,
        capture_output=True,
    )
    
    # Wait for services to be healthy
    print("[SETUP] Waiting for services to be healthy...")
    max_wait = 120  # 2 minutes
    elapsed = 0
    while elapsed < max_wait:
        result = subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "ps"],
            capture_output=True,
            text=True,
        )
        if "healthy" in result.stdout or "running" in result.stdout:
            # Give services a bit more time to fully initialize
            time.sleep(10)
            break
        time.sleep(5)
        elapsed += 5
    
    yield
    
    # Teardown: Stop services
    print("\n[TEARDOWN] Stopping Docker Compose services...")
    subprocess.run(
        ["docker-compose", "-f", docker_compose_file, "down"],
        check=False,
        capture_output=True,
    )


@pytest.fixture
def docker_compose_exec(docker_compose_file: str):
    """Helper fixture to execute commands in Docker Compose containers."""
    def _exec(service: str, command: List[str]) -> subprocess.CompletedProcess:
        """Execute command in service container."""
        cmd = ["docker-compose", "-f", docker_compose_file, "exec", "-T", service] + command
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    return _exec


@pytest.fixture
def service_health_checks() -> Dict[str, List[str]]:
    """Return health check commands for each service."""
    return {
        "postgres": ["pg_isready", "-U", "airflow"],
        "zookeeper": ["nc", "-z", "localhost", "2181"],
        "kafka": ["kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"],
        "airflow-webserver": ["curl", "--fail", "http://localhost:8080/health"],
    }


@pytest.fixture
def required_ports() -> Dict[str, int]:
    """Return required ports for services."""
    return {
        "airflow-webserver": 8080,
        "kafka": 9092,
        "zookeeper": 2181,
    }

