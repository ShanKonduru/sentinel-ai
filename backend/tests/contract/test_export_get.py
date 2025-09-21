"""
Contract test for GET /api/v1/export endpoint.

This test MUST FAIL before implementation is created.
Tests the GET export API contract according to data-retrieval-api.yaml.
"""

import pytest
import requests
from uuid import uuid4


class TestExportGetContract:
    """
    Contract tests for GET export endpoint.
    These tests define the expected behavior and MUST fail until implemented.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    ENDPOINT = f"{BASE_URL}/export"
    
    def test_export_get_with_agent_id_success(self):
        """
        Test successful GET export with required agent_id parameter.
        Expected: 200 OK with CSV content.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "text/csv"
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        assert ".csv" in response.headers["Content-Disposition"]
        
        # CSV content should contain headers
        csv_content = response.text
        assert "agent_id" in csv_content
        assert "timestamp" in csv_content
        assert "latency_ms" in csv_content
    
    def test_export_get_missing_required_agent_id(self):
        """
        Test GET export without required agent_id parameter.
        Expected: 400 Bad Request with validation error.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "agent_id" in response_data["error"].lower()
    
    def test_export_get_missing_required_start_date(self):
        """
        Test GET export without required start_date parameter.
        Expected: 400 Bad Request with validation error.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "start_date" in response_data["error"].lower()
    
    def test_export_get_invalid_agent_id_format(self):
        """
        Test GET export with invalid agent_id UUID format.
        Expected: 400 Bad Request with validation error.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": "not-a-valid-uuid",
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "agent_id" in response_data["error"].lower()
    
    def test_export_get_invalid_date_format(self):
        """
        Test GET export with invalid date format.
        Expected: 400 Bad Request with validation error.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "invalid-date-format",
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "date" in response_data["error"].lower()
    
    def test_export_get_end_date_before_start_date(self):
        """
        Test GET export with end_date before start_date.
        Expected: 400 Bad Request with validation error.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "2025-09-20T23:59:59Z",
                "end_date": "2025-09-20T00:00:00Z"  # End before start
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
    
    def test_export_get_non_existent_agent(self):
        """
        Test GET export for non-existent agent.
        Expected: 404 Not Found.
        """
        non_existent_id = str(uuid4())
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": non_existent_id,
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 404
        response_data = response.json()
        assert "error" in response_data
        assert "not found" in response_data["error"].lower()
    
    def test_export_get_with_optional_limit_parameter(self):
        """
        Test GET export with optional limit parameter.
        Expected: 200 OK with limited results.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T23:59:59Z",
                "limit": 100
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "text/csv"
    
    def test_export_get_empty_result_set(self):
        """
        Test GET export when no data exists for time range.
        Expected: 200 OK with headers only CSV.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "2020-01-01T00:00:00Z",
                "end_date": "2020-01-01T23:59:59Z"  # Past date with no data
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "text/csv"
        
        # Should still contain headers even with no data
        csv_content = response.text
        assert "agent_id" in csv_content  # Headers present


@pytest.mark.contract
class TestExportGetContractPerformance:
    """
    Performance contract tests for GET export functionality.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    ENDPOINT = f"{BASE_URL}/export"
    
    def test_export_get_response_time(self):
        """
        Test GET export response time for reasonable dataset.
        Expected: Response within 2 seconds for moderate datasets.
        """
        import time
        
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        start_time = time.time()
        response = requests.get(
            self.ENDPOINT,
            params={
                "agent_id": agent_id,
                "start_date": "2025-09-20T00:00:00Z",
                "end_date": "2025-09-20T01:00:00Z",  # 1 hour window
                "limit": 1000
            }
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time < 2.0, f"Export response time {response_time:.2f}s exceeds 2s requirement"