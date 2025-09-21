"""
Contract test for POST /api/v1/metrics endpoint.

This test MUST FAIL before implementation is created.
Tests the metrics collection API contract according to metrics-collection-api.yaml.
"""

import pytest
import requests
import json
from datetime import datetime, timezone
from uuid import uuid4


class TestMetricsPostContract:
    """
    Contract tests for metrics submission endpoint.
    These tests define the expected behavior and MUST fail until implemented.
    """
    
    BASE_URL = "http://localhost:5000/api/v1"
    ENDPOINT = f"{BASE_URL}/metrics"
    
    def test_submit_complete_metrics_success(self):
        """
        Test successful submission of complete metrics data.
        Expected: 201 Created with success response.
        """
        # Valid metrics payload
        metrics_data = {
            "agent_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_ms": 150.5,
            "throughput_req_per_min": 45.2,
            "cost_per_request": 0.002,
            "cpu_usage_percent": 75.3,
            "gpu_usage_percent": 82.1,
            "memory_usage_mb": 1024.5,
            "custom_metrics": {
                "model_tokens": 1500,
                "cache_hit_rate": 0.85
            }
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 201
        response_data = response.json()
        assert "success" in response_data
        assert response_data["success"] is True
        assert "metric_id" in response_data
        assert "timestamp" in response_data
    
    def test_submit_minimal_metrics_success(self):
        """
        Test submission with only required fields.
        Expected: 201 Created even with minimal data.
        """
        # Minimal valid payload - only agent_id and one metric
        metrics_data = {
            "agent_id": str(uuid4()),
            "latency_ms": 200.0
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["success"] is True
    
    def test_submit_invalid_agent_id_format(self):
        """
        Test submission with invalid agent_id format.
        Expected: 400 Bad Request with validation error.
        """
        metrics_data = {
            "agent_id": "not-a-valid-uuid",
            "latency_ms": 150.0
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "agent_id" in response_data["error"].lower()
    
    def test_submit_no_metrics_data(self):
        """
        Test submission with agent_id but no actual metrics.
        Expected: 400 Bad Request - at least one metric required.
        """
        metrics_data = {
            "agent_id": str(uuid4())
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "metric" in response_data["error"].lower()
    
    def test_submit_invalid_percentage_values(self):
        """
        Test submission with percentage values outside 0-100 range.
        Expected: 400 Bad Request with validation error.
        """
        metrics_data = {
            "agent_id": str(uuid4()),
            "cpu_usage_percent": 150.0,  # Invalid: > 100
            "gpu_usage_percent": -10.0   # Invalid: < 0
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
    
    def test_submit_negative_latency(self):
        """
        Test submission with negative latency value.
        Expected: 400 Bad Request - latency must be positive.
        """
        metrics_data = {
            "agent_id": str(uuid4()),
            "latency_ms": -50.0  # Invalid: negative latency
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "latency" in response_data["error"].lower()
    
    def test_submit_future_timestamp(self):
        """
        Test submission with timestamp in the future.
        Expected: 400 Bad Request - timestamps cannot be in future.
        """
        # Future timestamp (1 hour ahead)
        future_time = datetime.now(timezone.utc)
        future_time = future_time.replace(hour=future_time.hour + 1)
        
        metrics_data = {
            "agent_id": str(uuid4()),
            "timestamp": future_time.isoformat(),
            "latency_ms": 100.0
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "timestamp" in response_data["error"].lower()
    
    def test_submit_empty_request_body(self):
        """
        Test submission with empty request body.
        Expected: 400 Bad Request.
        """
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
    
    def test_submit_malformed_json(self):
        """
        Test submission with malformed JSON.
        Expected: 400 Bad Request.
        """
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            data="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        
        # Contract expectations
        assert response.status_code == 400
    
    def test_content_type_validation(self):
        """
        Test that endpoint requires proper Content-Type header.
        Expected: 400 Bad Request for non-JSON content type.
        """
        metrics_data = {
            "agent_id": str(uuid4()),
            "latency_ms": 150.0
        }
        
        # This WILL FAIL until metrics API is implemented
        response = requests.post(
            self.ENDPOINT,
            data=json.dumps(metrics_data),
            headers={"Content-Type": "text/plain"}
        )
        
        # Contract expectations
        assert response.status_code == 400


# Integration helper for testing
@pytest.fixture(scope="session")
def metrics_api_server():
    """
    Fixture to ensure metrics API server is running.
    Will be implemented when we create the Flask app.
    """
    # TODO: Start/stop metrics API server for testing
    # For now, tests will fail because server doesn't exist yet
    yield "http://localhost:5000"


@pytest.mark.contract
class TestMetricsPostContractIntegration:
    """
    Integration contract tests that verify the endpoint works with database.
    These also MUST fail until implementation is complete.
    """
    
    def test_metrics_persisted_to_database(self, metrics_api_server):
        """
        Test that submitted metrics are actually stored in database.
        This is an integration test that verifies end-to-end functionality.
        """
        agent_id = str(uuid4())
        metrics_data = {
            "agent_id": agent_id,
            "latency_ms": 125.0,
            "cpu_usage_percent": 65.5
        }
        
        # Submit metrics - WILL FAIL until implemented
        response = requests.post(
            f"{metrics_api_server}/api/v1/metrics",
            json=metrics_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        
        # Verify metrics can be retrieved (assumes GET endpoint exists)
        # This tests integration with database layer
        get_response = requests.get(
            f"{metrics_api_server}/api/v1/metrics?agent_id={agent_id}"
        )
        
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        assert len(retrieved_data["metrics"]) > 0
        assert retrieved_data["metrics"][0]["latency_ms"] == 125.0