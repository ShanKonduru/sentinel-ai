"""
Contract test for GET /api/v1/agents endpoint.

This test MUST FAIL before implementation is created.
Tests the agents retrieval API contract according to data-retrieval-api.yaml.
"""

import pytest
import requests
from uuid import uuid4


class TestAgentsGetContract:
    """
    Contract tests for agents listing endpoint.
    These tests define the expected behavior and MUST fail until implemented.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    ENDPOINT = f"{BASE_URL}/agents"
    
    def test_get_all_agents_success(self):
        """
        Test successful retrieval of all agents.
        Expected: 200 OK with agents array.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "agents" in response_data
        assert isinstance(response_data["agents"], list)
        assert "total" in response_data
        assert "page" in response_data
        assert "limit" in response_data
        
        # Each agent should have required fields
        for agent in response_data["agents"]:
            assert "agent_id" in agent
            assert "name" in agent
            assert "status" in agent
            assert "created_at" in agent
            assert agent["status"] in ["running", "stopped", "error", "unknown"]
    
    def test_get_agents_with_status_filter(self):
        """
        Test filtering agents by status.
        Expected: 200 OK with filtered results.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={"status": "running"}
        )
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "agents" in response_data
        
        # All returned agents should have the specified status
        for agent in response_data["agents"]:
            assert agent["status"] == "running"
    
    def test_get_agents_with_pagination(self):
        """
        Test pagination parameters.
        Expected: 200 OK with proper pagination metadata.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "limit": 10,
                "offset": 0
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "agents" in response_data
        assert len(response_data["agents"]) <= 10
        assert response_data["limit"] == 10
        assert response_data["offset"] == 0
        assert "total" in response_data
    
    def test_get_agents_invalid_status_filter(self):
        """
        Test invalid status filter value.
        Expected: 400 Bad Request with validation error.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={"status": "invalid_status"}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "status" in response_data["error"].lower()
    
    def test_get_agents_invalid_pagination_params(self):
        """
        Test invalid pagination parameters.
        Expected: 400 Bad Request for negative values.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={
                "limit": -1,
                "offset": -5
            }
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
    
    def test_get_agents_limit_too_large(self):
        """
        Test limit parameter exceeding maximum allowed.
        Expected: 400 Bad Request for limit > 100.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={"limit": 500}
        )
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "limit" in response_data["error"].lower()
    
    def test_get_agents_empty_result_set(self):
        """
        Test handling when no agents match criteria.
        Expected: 200 OK with empty agents array.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(
            self.ENDPOINT,
            params={"status": "error"}  # Assuming no error agents exist
        )
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "agents" in response_data
        assert isinstance(response_data["agents"], list)
        assert response_data["total"] >= 0


class TestAgentByIdContract:
    """
    Contract tests for individual agent retrieval.
    Tests GET /api/v1/agents/{agent_id} endpoint.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def test_get_agent_by_id_success(self):
        """
        Test successful retrieval of specific agent.
        Expected: 200 OK with agent details.
        """
        # Use a sample agent ID (would exist in real implementation)
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(f"{self.BASE_URL}/agents/{agent_id}")
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "agent_id" in response_data
        assert "name" in response_data
        assert "description" in response_data
        assert "status" in response_data
        assert "created_at" in response_data
        assert "last_seen" in response_data
        assert "metadata" in response_data
        assert response_data["agent_id"] == agent_id
    
    def test_get_agent_by_id_not_found(self):
        """
        Test retrieval of non-existent agent.
        Expected: 404 Not Found.
        """
        non_existent_id = str(uuid4())
        
        # This WILL FAIL until data API is implemented
        response = requests.get(f"{self.BASE_URL}/agents/{non_existent_id}")
        
        # Contract expectations
        assert response.status_code == 404
        response_data = response.json()
        assert "error" in response_data
        assert "not found" in response_data["error"].lower()
    
    def test_get_agent_invalid_id_format(self):
        """
        Test invalid agent ID format.
        Expected: 400 Bad Request with validation error.
        """
        invalid_id = "not-a-valid-uuid"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(f"{self.BASE_URL}/agents/{invalid_id}")
        
        # Contract expectations
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data
        assert "agent_id" in response_data["error"].lower()


class TestAgentMetricsContract:
    """
    Contract tests for agent-specific metrics endpoint.
    Tests GET /api/v1/agents/{agent_id}/metrics endpoint.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def test_get_agent_metrics_success(self):
        """
        Test successful retrieval of agent-specific metrics.
        Expected: 200 OK with metrics for specific agent.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(f"{self.BASE_URL}/agents/{agent_id}/metrics")
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "metrics" in response_data
        assert "agent_id" in response_data
        assert response_data["agent_id"] == agent_id
        assert "total" in response_data
        
        # All metrics should be for the specified agent
        for metric in response_data["metrics"]:
            assert metric["agent_id"] == agent_id
    
    def test_get_agent_metrics_with_time_range(self):
        """
        Test agent metrics with time filtering.
        Expected: 200 OK with time-filtered metrics.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        start_time = "2025-09-20T00:00:00Z"
        end_time = "2025-09-20T23:59:59Z"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            f"{self.BASE_URL}/agents/{agent_id}/metrics",
            params={
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "metrics" in response_data
        assert response_data["agent_id"] == agent_id
    
    def test_get_agent_metrics_not_found(self):
        """
        Test metrics for non-existent agent.
        Expected: 404 Not Found.
        """
        non_existent_id = str(uuid4())
        
        # This WILL FAIL until data API is implemented
        response = requests.get(f"{self.BASE_URL}/agents/{non_existent_id}/metrics")
        
        # Contract expectations
        assert response.status_code == 404
        response_data = response.json()
        assert "error" in response_data
        assert "not found" in response_data["error"].lower()
    
    def test_get_agent_metrics_with_aggregation(self):
        """
        Test agent metrics with aggregation.
        Expected: 200 OK with aggregated metrics for agent.
        """
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        response = requests.get(
            f"{self.BASE_URL}/agents/{agent_id}/metrics",
            params={
                "aggregate": "hour",
                "start_time": "2025-09-20T00:00:00Z",
                "end_time": "2025-09-20T23:59:59Z"
            }
        )
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "aggregated_metrics" in response_data
        assert "interval" in response_data
        assert response_data["interval"] == "hour"
        assert response_data["agent_id"] == agent_id


@pytest.mark.contract
class TestAgentsContractPerformance:
    """
    Performance contract tests for agents endpoints.
    Verify performance requirements from the specification.
    """
    
    BASE_URL = "http://localhost:8000/api/v1"
    ENDPOINT = f"{BASE_URL}/agents"
    
    def test_get_agents_response_time_under_50ms(self):
        """
        Test that agents listing responds within 50ms requirement.
        Expected: Response time < 50ms.
        """
        import time
        
        # This WILL FAIL until data API is implemented
        start_time = time.time()
        response = requests.get(self.ENDPOINT)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time_ms < 50, f"Response time {response_time_ms:.2f}ms exceeds 50ms requirement"
    
    def test_get_agent_by_id_performance(self):
        """
        Test individual agent retrieval performance.
        Expected: Response time < 50ms.
        """
        import time
        
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # This WILL FAIL until data API is implemented
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/agents/{agent_id}")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time_ms < 50, f"Response time {response_time_ms:.2f}ms exceeds 50ms requirement"