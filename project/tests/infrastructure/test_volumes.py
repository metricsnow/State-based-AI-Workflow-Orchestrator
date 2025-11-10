"""
Tests for volume persistence and data storage.
"""
import subprocess
import pytest
import time


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.volume
class TestVolumePersistence:
    """Test that volumes persist data correctly."""
    
    def test_postgres_volume_persistence(self, docker_compose_file: str):
        """Test that PostgreSQL data persists across restarts."""
        # Create a test table
        create_result = subprocess.run(
            [
                "docker-compose", "-f", docker_compose_file, "exec", "-T",
                "postgres", "psql", "-U", "airflow", "-d", "airflow",
                "-c", "CREATE TABLE IF NOT EXISTS test_persistence (id INT PRIMARY KEY, data TEXT);"
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        
        # Insert test data
        insert_result = subprocess.run(
            [
                "docker-compose", "-f", docker_compose_file, "exec", "-T",
                "postgres", "psql", "-U", "airflow", "-d", "airflow",
                "-c", "INSERT INTO test_persistence (id, data) VALUES (1, 'test_data') ON CONFLICT (id) DO NOTHING;"
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        
        # Restart postgres service
        subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "restart", "postgres"],
            capture_output=True,
            check=False,
        )
        
        # Wait for service to be ready
        time.sleep(10)
        
        # Verify data still exists
        verify_result = subprocess.run(
            [
                "docker-compose", "-f", docker_compose_file, "exec", "-T",
                "postgres", "psql", "-U", "airflow", "-d", "airflow",
                "-c", "SELECT * FROM test_persistence WHERE id = 1;"
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        
        assert "test_data" in verify_result.stdout, \
            "PostgreSQL volume persistence test failed - data not found after restart"
    
    def test_volume_exists(self, docker_compose_file: str):
        """Test that required volumes exist."""
        result = subprocess.run(
            ["docker", "volume", "ls"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Check for postgres_data volume (name includes project directory)
        assert "postgres" in result.stdout.lower() or "data" in result.stdout.lower(), \
            "PostgreSQL volume not found"

