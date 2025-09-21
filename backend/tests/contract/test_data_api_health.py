"""
Contract test for Data API GET /api/v1/health endpoint.

This test MUST FAIL before implementation is created.
Tests the Data API health check contract according to data-retrieval-api.yaml.
"""

import pytest
import requests
import time


class TestDataApiHealthCheckContract:
    """
    Contract tests for Data API health check endpoint.
    These tests define the expected behavior and MUST fail until implemented.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    HEALTH_ENDPOINT = f"{BASE_URL}/health"
    
    def test_data_api_health_check_success(self):
        """
        Test successful Data API health check.
        Expected: 200 OK with status information.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.HEALTH_ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "application/json"
        
        health_data = response.json()
        assert "status" in health_data
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "service" in health_data
        assert health_data["service"] == "data-api"
        assert "version" in health_data
    
    def test_data_api_health_check_with_dependencies(self):
        """
        Test Data API health check includes database dependency status.
        Expected: 200 OK with database connectivity info.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.HEALTH_ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        health_data = response.json()
        
        # Should include dependency information
        assert "dependencies" in health_data
        dependencies = health_data["dependencies"]
        assert "database" in dependencies
        assert "status" in dependencies["database"]
        assert dependencies["database"]["status"] in ["healthy", "unhealthy"]
    
    def test_data_api_health_check_response_time(self):
        """
        Test Data API health check response time.
        Expected: Response within 100ms for health checks.
        """
        # This WILL FAIL until data API is implemented
        start_time = time.time()
        response = requests.get(self.HEALTH_ENDPOINT)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time < 0.1, f"Health check response time {response_time:.3f}s exceeds 100ms requirement"
    
    def test_data_api_health_check_content_structure(self):
        """
        Test Data API health check response structure matches contract.
        Expected: Specific JSON schema compliance.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.HEALTH_ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        health_data = response.json()
        
        # Validate required fields
        required_fields = ["status", "timestamp", "service", "version", "dependencies"]
        for field in required_fields:
            assert field in health_data, f"Required field '{field}' missing from health response"
        
        # Validate timestamp format (ISO 8601)
        timestamp = health_data["timestamp"]
        assert isinstance(timestamp, str)
        # Basic ISO format validation (more detailed validation would use datetime parsing)
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp or "-" in timestamp[-6:]
    
    def test_data_api_health_check_service_identification(self):
        """
        Test Data API health check correctly identifies service.
        Expected: Service field distinguishes from metrics API.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.HEALTH_ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        health_data = response.json()
        
        # Must identify as data-api (not metrics-api)
        assert health_data["service"] == "data-api"
        assert health_data["service"] != "metrics-api"


@pytest.mark.contract
class TestDataApiHealthCheckContractConsistency:
    """
    Contract tests for Data API health check consistency with Metrics API.
    Tests cross-service health check compatibility.
    """
    
    DATA_API_HEALTH = "http://localhost:8000/api/v1/health"
    METRICS_API_HEALTH = "http://localhost:5000/health"
    
    def test_health_check_schema_consistency(self):
        """
        Test that both APIs return compatible health check schemas.
        Expected: Both services use consistent health check format.
        """
        # This WILL FAIL until both APIs are implemented
        data_response = requests.get(self.DATA_API_HEALTH)
        metrics_response = requests.get(self.METRICS_API_HEALTH)
        
        # Both should succeed
        assert data_response.status_code == 200
        assert metrics_response.status_code == 200
        
        data_health = data_response.json()
        metrics_health = metrics_response.json()
        
        # Both should have consistent core fields
        common_fields = ["status", "timestamp", "service"]
        for field in common_fields:
            assert field in data_health, f"Data API missing field: {field}"
            assert field in metrics_health, f"Metrics API missing field: {field}"
        
        # Services should be properly identified
        assert data_health["service"] == "data-api"
        assert metrics_health["service"] == "metrics-api"
    
    def test_cross_service_health_timing(self):
        """
        Test that both health checks respond within acceptable time.
        Expected: Both services meet performance requirements.
        """
        # This WILL FAIL until both APIs are implemented
        start_time = time.time()
        
        # Check both services concurrently (simplified here)
        data_response = requests.get(self.DATA_API_HEALTH)
        metrics_response = requests.get(self.METRICS_API_HEALTH)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Contract expectations
        assert data_response.status_code == 200
        assert metrics_response.status_code == 200
        assert total_time < 0.2, f"Combined health checks took {total_time:.3f}s, exceeds 200ms requirement"
    
    def test_health_check_status_values(self):
        """
        Test that health status values are standardized across services.
        Expected: Consistent status vocabulary.
        """
        # This WILL FAIL until both APIs are implemented
        data_response = requests.get(self.DATA_API_HEALTH)
        metrics_response = requests.get(self.METRICS_API_HEALTH)
        
        # Contract expectations
        assert data_response.status_code == 200
        assert metrics_response.status_code == 200
        
        data_health = data_response.json()
        metrics_health = metrics_response.json()
        
        # Status values should be from allowed set
        allowed_statuses = ["healthy", "unhealthy", "degraded"]
        assert data_health["status"] in allowed_statuses
        assert metrics_health["status"] in allowed_statuses