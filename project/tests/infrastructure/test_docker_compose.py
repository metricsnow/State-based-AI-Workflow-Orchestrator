"""
Tests for Docker Compose configuration and setup.
"""
import os
import subprocess
import pytest
from pathlib import Path


def get_root_dir() -> Path:
    """Get the repository root directory."""
    # Navigate from project/tests/infrastructure/ to root/
    return Path(__file__).parent.parent.parent.parent


@pytest.mark.docker
class TestDockerComposeConfig:
    """Test Docker Compose file configuration."""
    
    def test_docker_compose_file_exists(self, docker_compose_file: str):
        """Test that docker-compose.yml exists."""
        # Also check with direct path resolution
        root_dir = get_root_dir()
        compose_file = root_dir / "docker-compose.yml"
        assert compose_file.exists() or os.path.exists(docker_compose_file), \
            f"Docker Compose file not found: {docker_compose_file} or {compose_file}"
    
    def test_docker_compose_syntax_valid(self, docker_compose_file: str):
        """Test that Docker Compose file has valid syntax."""
        root_dir = get_root_dir()
        compose_file = root_dir / "docker-compose.yml"
        compose_path = str(compose_file) if compose_file.exists() else docker_compose_file
        
        result = subprocess.run(
            ["docker-compose", "-f", compose_path, "config"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Docker Compose syntax error: {result.stderr}"
    
    def test_all_services_defined(self, docker_compose_file: str, docker_compose_services: list):
        """Test that all required services are defined."""
        root_dir = get_root_dir()
        compose_file = root_dir / "docker-compose.yml"
        compose_path = str(compose_file) if compose_file.exists() else docker_compose_file
        
        result = subprocess.run(
            ["docker-compose", "-f", compose_path, "config"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        for service in docker_compose_services:
            assert f"  {service}:" in result.stdout or f"    {service}:" in result.stdout, \
                f"Service '{service}' not found in docker-compose.yml"
    
    def test_env_file_exists(self, env_file: str):
        """Test that .env file exists."""
        # Also check with direct path resolution
        root_dir = get_root_dir()
        env_path = root_dir / ".env"
        assert env_path.exists() or os.path.exists(env_file), \
            f".env file not found: {env_file} or {env_path}"
    
    def test_env_file_has_fernet_key(self, env_file: str):
        """Test that .env file contains FERNET_KEY."""
        root_dir = get_root_dir()
        env_path = root_dir / ".env"
        # Try both paths
        env_file_path = env_path if env_path.exists() else env_file
        if not os.path.exists(env_file_path):
            pytest.skip(f".env file not found at {env_file_path}")
        
        with open(env_file_path, "r") as f:
            content = f.read()
            assert "FERNET_KEY=" in content, "FERNET_KEY not found in .env file"
            # Check that it's not the placeholder
            assert "your_fernet_key_here" not in content, "FERNET_KEY is still a placeholder"


@pytest.mark.docker
class TestDirectoryStructure:
    """Test required directory structure."""
    
    def test_dags_directory_exists(self):
        """Test that dags directory exists."""
        # Navigate from project/tests/infrastructure/ to project/dags
        base_path = Path(__file__).parent.parent.parent
        dags_dir = base_path / "dags"
        assert dags_dir.exists(), "project/dags directory not found"
        assert dags_dir.is_dir(), "project/dags is not a directory"
    
    def test_logs_directory_exists(self):
        """Test that logs directory exists."""
        base_path = Path(__file__).parent.parent.parent
        logs_dir = base_path / "logs"
        assert logs_dir.exists(), "project/logs directory not found"
        assert logs_dir.is_dir(), "project/logs is not a directory"
    
    def test_plugins_directory_exists(self):
        """Test that plugins directory exists."""
        base_path = Path(__file__).parent.parent.parent
        plugins_dir = base_path / "plugins"
        assert plugins_dir.exists(), "project/plugins directory not found"
        assert plugins_dir.is_dir(), "project/plugins is not a directory"


@pytest.mark.docker
class TestDockerInstallation:
    """Test Docker and Docker Compose installation."""
    
    def test_docker_installed(self):
        """Test that Docker is installed."""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Docker is not installed or not in PATH"
    
    def test_docker_compose_installed(self):
        """Test that Docker Compose is installed."""
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Docker Compose is not installed or not in PATH"
    
    def test_docker_daemon_running(self):
        """Test that Docker daemon is running."""
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Docker ps should succeed even if no containers are running
        assert result.returncode == 0, "Docker daemon is not running"

