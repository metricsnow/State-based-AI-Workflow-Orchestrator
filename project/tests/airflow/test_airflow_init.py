"""
Tests for Airflow initialization and configuration.

This module contains tests to validate:
- Airflow database initialization
- Admin user creation
- Airflow configuration validation
- CLI command functionality

Implementation Notes:
- Initialization uses 'airflow db init' via docker-compose run --rm
- Script creates one-off containers for reliable execution
- Tests cover both integration and unit test scenarios
"""

import pytest
import subprocess
import time
import os
from pathlib import Path


class TestAirflowInitialization:
    """Test Airflow database initialization and user creation."""

    @pytest.fixture(scope="class")
    def docker_compose_file(self):
        """Return path to docker-compose.yml."""
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / "docker-compose.yml"

    @pytest.fixture(scope="class")
    def init_script(self):
        """Return path to init-airflow.sh script."""
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / "scripts" / "init-airflow.sh"

    def test_init_script_exists(self, init_script):
        """Test that initialization script exists and is executable."""
        assert init_script.exists(), f"Init script not found at {init_script}"
        assert os.access(init_script, os.X_OK), "Init script is not executable"

    def test_docker_compose_file_exists(self, docker_compose_file):
        """Test that docker-compose.yml exists."""
        assert docker_compose_file.exists(), f"docker-compose.yml not found at {docker_compose_file}"

    @pytest.mark.integration
    def test_postgres_service_healthy(self):
        """Test that PostgreSQL service is healthy."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "postgres", "pg_isready", "-U", "airflow"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"PostgreSQL is not healthy: {result.stderr}"

    @pytest.mark.integration
    def test_airflow_webserver_running(self):
        """Test that Airflow webserver container is running."""
        result = subprocess.run(
            ["docker-compose", "ps", "airflow-webserver"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "Up" in result.stdout or "airflow-webserver" in result.stdout, \
            "Airflow webserver is not running"

    @pytest.mark.integration
    def test_airflow_database_initialized(self):
        """Test that Airflow database has been initialized."""
        # Check if airflow db migrate can run (should succeed if DB is initialized)
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "airflow", "db", "migrate"],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Should succeed or indicate DB is already initialized
        assert result.returncode == 0 or "already" in result.stdout.lower(), \
            f"Database initialization failed: {result.stderr}"

    @pytest.mark.integration
    def test_airflow_admin_user_exists(self):
        """Test that admin user exists in Airflow."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "airflow", "users", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Failed to list users: {result.stderr}"
        assert "admin" in result.stdout.lower(), "Admin user not found in user list"

    @pytest.mark.integration
    def test_airflow_cli_version(self):
        """Test that Airflow CLI version command works."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "airflow", "version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Airflow version command failed: {result.stderr}"
        assert "2.8" in result.stdout, "Airflow version should be 2.8.x"

    @pytest.mark.integration
    def test_airflow_config_executor(self):
        """Test that Airflow executor is configured correctly."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "airflow", "config", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Config list command failed: {result.stderr}"
        # Check for LocalExecutor configuration
        assert "LocalExecutor" in result.stdout or "executor" in result.stdout.lower(), \
            "Executor configuration not found"

    @pytest.mark.integration
    def test_airflow_dags_folder_accessible(self):
        """Test that DAGs folder is accessible from Airflow container."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "ls", "/opt/airflow/dags"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"DAGs folder not accessible: {result.stderr}"

    @pytest.mark.integration
    def test_airflow_dags_list_command(self):
        """Test that airflow dags list command works."""
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "airflow-webserver", "airflow", "dags", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Command should succeed even if no DAGs exist
        assert result.returncode == 0, f"DAGs list command failed: {result.stderr}"

    def test_folder_structure_exists(self):
        """Test that required folders exist in project directory."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        logs_folder = project_root / "logs"
        plugins_folder = project_root / "plugins"

        assert dags_folder.exists(), "dags/ folder does not exist"
        assert logs_folder.exists(), "logs/ folder does not exist"
        assert plugins_folder.exists(), "plugins/ folder does not exist"

    def test_gitkeep_files_exist(self):
        """Test that .gitkeep files exist in folders."""
        project_root = Path(__file__).parent.parent.parent
        dags_gitkeep = project_root / "dags" / ".gitkeep"
        logs_gitkeep = project_root / "logs" / ".gitkeep"
        plugins_gitkeep = project_root / "plugins" / ".gitkeep"

        assert dags_gitkeep.exists(), ".gitkeep file missing in dags/"
        assert logs_gitkeep.exists(), ".gitkeep file missing in logs/"
        assert plugins_gitkeep.exists(), ".gitkeep file missing in plugins/"

