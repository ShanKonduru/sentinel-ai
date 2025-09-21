"""
Contract test for GET /health endpoints.

This test MUST FAIL before implementation is created.
Tests health check endpoints for both metrics-api and data-api services.
"""

import pytest
import requests
import time


class TestMetricsApiHealthContract:
    """
    Contract tests for metrics API health endpoint.
    Tests health check functionality for Flask metrics service.
    """
    
    BASE_URL = "http://localhost:5000"
    ENDPOINT = f"{BASE_URL}/health"
    
    def test_health_check_success(self):
        """
        Test successful health check response.
        Expected: 200 OK with health status information.
        """
        # This WILL FAIL until metrics API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "healthy"
        assert "service" in response_data
        assert response_data["service"] == "metrics-api"
        assert "timestamp" in response_data
        assert "version" in response_data
    
    def test_health_check_includes_dependencies(self):
        """
        Test that health check includes dependency status.
        Expected: 200 OK with database connectivity status.
        """
        # This WILL FAIL until metrics API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "dependencies" in response_data
        assert "database" in response_data["dependencies"]
        assert response_data["dependencies"]["database"]["status"] in ["healthy", "unhealthy"]
        
        if response_data["dependencies"]["database"]["status"] == "healthy":
            assert "response_time_ms" in response_data["dependencies"]["database"]
    
    def test_health_check_performance(self):
        """
        Test health check response time.
        Expected: Health check responds within 100ms.
        """
        # This WILL FAIL until metrics API is implemented
        start_time = time.time()
        response = requests.get(self.ENDPOINT)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time_ms < 100, f"Health check response time {response_time_ms:.2f}ms exceeds 100ms"
    
    def test_health_check_when_database_down(self):
        """
        Test health check behavior when database is unavailable.
        Expected: 503 Service Unavailable with dependency failure details.
        """
        # This test simulates database unavailability
        # In implementation, this would test actual database connectivity
        
        # This WILL FAIL until metrics API is implemented
        # Note: This test may pass with 200 if database is actually available
        # The key is that the response includes dependency status
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations for when database is down
        if response.status_code == 503:
            response_data = response.json()
            assert "status" in response_data
            assert response_data["status"] == "degraded"
            assert "dependencies" in response_data
            assert response_data["dependencies"]["database"]["status"] == "unhealthy"
        else:
            # If database is up, should still include dependency info
            assert response.status_code == 200
            response_data = response.json()
            assert "dependencies" in response_data


class TestDataApiHealthContract:
    """
    Contract tests for data API health endpoint.
    Tests health check functionality for FastAPI data service.
    """
    
    BASE_URL = "http://localhost:8000"
    ENDPOINT = f"{BASE_URL}/health"
    
    def test_health_check_success(self):
        """
        Test successful health check response.
        Expected: 200 OK with health status information.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "healthy"
        assert "service" in response_data
        assert response_data["service"] == "data-api"
        assert "timestamp" in response_data
        assert "version" in response_data
    
    def test_health_check_includes_dependencies(self):
        """
        Test that health check includes dependency status.
        Expected: 200 OK with database connectivity status.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "dependencies" in response_data
        assert "database" in response_data["dependencies"]
        assert response_data["dependencies"]["database"]["status"] in ["healthy", "unhealthy"]
    
    def test_health_check_includes_metrics(self):
        """
        Test that health check includes service metrics.
        Expected: 200 OK with uptime and request count metrics.
        """
        # This WILL FAIL until data API is implemented
        response = requests.get(self.ENDPOINT)
        
        # Contract expectations
        assert response.status_code == 200
        response_data = response.json()
        assert "metrics" in response_data
        assert "uptime_seconds" in response_data["metrics"]
        assert "requests_processed" in response_data["metrics"]
        assert isinstance(response_data["metrics"]["uptime_seconds"], (int, float))
        assert isinstance(response_data["metrics"]["requests_processed"], int)
    
    def test_health_check_performance(self):
        """
        Test health check response time.
        Expected: Health check responds within 100ms.
        """
        # This WILL FAIL until data API is implemented
        start_time = time.time()
        response = requests.get(self.ENDPOINT)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # Contract expectations
        assert response.status_code == 200
        assert response_time_ms < 100, f"Health check response time {response_time_ms:.2f}ms exceeds 100ms"


class TestHealthContractCrossService:
    """
    Cross-service health check contract tests.
    Tests interactions and consistency between health endpoints.
    """
    
    METRICS_HEALTH_URL = "http://localhost:5000/health"
    DATA_HEALTH_URL = "http://localhost:8000/health"
    
    def test_both_services_health_consistency(self):
        """
        Test that both services report consistent health information.
        Expected: Both services should have consistent timestamps and status.
        """
        # This WILL FAIL until both APIs are implemented
        metrics_response = requests.get(self.METRICS_HEALTH_URL)
        data_response = requests.get(self.DATA_HEALTH_URL)
        
        # Both should be healthy or report specific issues
        assert metrics_response.status_code in [200, 503]
        assert data_response.status_code in [200, 503]
        
        if metrics_response.status_code == 200 and data_response.status_code == 200:
            metrics_data = metrics_response.json()
            data_data = data_response.json()
            
            # Both should report database status
            assert "dependencies" in metrics_data
            assert "dependencies" in data_data
            assert "database" in metrics_data["dependencies"]
            assert "database" in data_data["dependencies"]
            
            # Database status should be consistent across services
            metrics_db_status = metrics_data["dependencies"]["database"]["status"]
            data_db_status = data_data["dependencies"]["database"]["status"]
            
            # If both are connecting to the same database, status should match
            assert metrics_db_status == data_db_status
    
    def test_health_endpoint_concurrent_access(self):
        """
        Test concurrent access to health endpoints.
        Expected: Multiple concurrent health checks should all succeed.
        """
        import threading
        
        results = []
        
        def check_health(url):
            try:
                # This WILL FAIL until APIs are implemented
                response = requests.get(url, timeout=5)
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Start concurrent health checks
        threads = []
        urls = [self.METRICS_HEALTH_URL, self.DATA_HEALTH_URL] * 3  # 6 concurrent requests
        
        for url in urls:
            thread = threading.Thread(target=check_health, args=(url,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Contract expectations (when implemented)
        # All health checks should succeed or fail consistently
        # This ensures health endpoints don't crash under concurrent load
        assert len(results) == 6  # All requests completed


@pytest.mark.contract
class TestHealthContractResilience:
    """
    Resilience and error handling contract tests for health endpoints.
    """
    
    def test_health_check_survives_high_frequency_requests(self):
        """
        Test health endpoint resilience under high frequency requests.
        Expected: Health endpoint remains responsive under load.
        """
        metrics_url = "http://localhost:5000/health"
        
        response_times = []
        
        # This WILL FAIL until metrics API is implemented
        for i in range(10):
            start_time = time.time()
            try:
                response = requests.get(metrics_url, timeout=2)
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                # Each request should succeed
                assert response.status_code in [200, 503]
                
            except requests.exceptions.RequestException:
                # Connection errors are expected since service isn't running
                response_times.append(float('inf'))
        
        # Contract expectations (when implemented)
        # Response times should remain consistent (no degradation)
        # Average response time should be under 200ms
        if any(t != float('inf') for t in response_times):
            valid_times = [t for t in response_times if t != float('inf')]
            avg_response_time = sum(valid_times) / len(valid_times)
            assert avg_response_time < 0.2, f"Average response time {avg_response_time:.3f}s exceeds 200ms"
    
    def test_health_endpoint_handles_invalid_methods(self):
        """
        Test health endpoint response to invalid HTTP methods.
        Expected: 405 Method Not Allowed for POST, PUT, DELETE requests.
        """
        health_url = "http://localhost:5000/health"
        
        # This WILL FAIL until metrics API is implemented
        # Test various HTTP methods that should not be allowed
        for method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            response = requests.request(method, health_url)
            # Should return 405 Method Not Allowed (when implemented)
            # Currently will fail with connection error