"""
Integration test for Performance Diagnosis user scenario.

This test simulates the complete workflow of an AI engineer diagnosing
performance issues through the system's APIs. Tests end-to-end integration
of metrics collection, storage, retrieval, and analysis.

Based on Journey 1 from quickstart.md - MUST FAIL before implementation.
"""

import pytest
import requests
import time
from datetime import datetime, timedelta
from uuid import uuid4


class TestPerformanceDiagnosisIntegration:
    """
    Integration tests for AI engineer performance diagnosis workflow.
    These tests simulate the complete user journey and MUST fail until implemented.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    AGENT_ID = "550e8400-e29b-41d4-a716-446655440000"
    
    def test_performance_diagnosis_complete_workflow(self):
        """
        Test complete performance diagnosis workflow.
        Simulates AI engineer investigating slow agent response times.
        """
        # This WILL FAIL until both APIs are implemented and connected
        
        # Step 1: Engineer notices slow response and starts investigation
        # Simulate submitting current performance metrics showing high latency
        
        current_time = datetime.utcnow()
        problem_metrics = {
            "agent_id": self.AGENT_ID,
            "timestamp": current_time.isoformat() + "Z",
            "latency_ms": 2500,  # High latency indicating problem
            "cpu_usage_percent": 95,
            "memory_usage_mb": 8192,
            "throughput_req_per_min": 10  # Low throughput due to performance issue
        }
        
        metrics_response = requests.post(
            f"{self.METRICS_API_BASE}/metrics",
            json=problem_metrics
        )
        
        # Should successfully submit metrics
        assert metrics_response.status_code == 201
        submission_result = metrics_response.json()
        assert "id" in submission_result
        assert submission_result["status"] == "accepted"
        
        # Step 2: Engineer queries recent metrics to confirm issue
        # Allow time for metrics to be processed and stored
        time.sleep(1)
        
        # Query recent metrics for this agent
        recent_query_params = {
            "agent_id": self.AGENT_ID,
            "start_date": (current_time - timedelta(minutes=5)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "limit": 50
        }
        
        recent_metrics_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=recent_query_params
        )
        
        # Should successfully retrieve recent metrics
        assert recent_metrics_response.status_code == 200
        recent_data = recent_metrics_response.json()
        assert "metrics" in recent_data
        assert len(recent_data["metrics"]) > 0
        
        # Verify the problematic metrics are present
        found_problem_metric = False
        for metric in recent_data["metrics"]:
            if metric["latency_ms"] == 2500:
                found_problem_metric = True
                assert metric["agent_id"] == self.AGENT_ID
                assert metric["cpu_usage_percent"] == 95
                assert metric["memory_usage_mb"] == 8192
                break
        
        assert found_problem_metric, "Problem metrics not found in recent data"
        
        # Step 3: Engineer analyzes historical data to identify pattern
        # Query last hour of data to see if this is a trend
        
        historical_query_params = {
            "agent_id": self.AGENT_ID,
            "start_date": (current_time - timedelta(hours=1)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "aggregation": "5m"  # 5-minute aggregation
        }
        
        historical_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=historical_query_params
        )
        
        # Should successfully retrieve historical data
        assert historical_response.status_code == 200
        historical_data = historical_response.json()
        assert "metrics" in historical_data
        
        # Step 4: Engineer correlates metrics to identify root cause
        # Verify we can identify correlation between memory and latency
        
        high_latency_count = 0
        high_memory_count = 0
        
        for metric in historical_data["metrics"]:
            if metric.get("latency_ms", 0) > 1000:  # High latency threshold
                high_latency_count += 1
            if metric.get("memory_usage_mb", 0) > 6000:  # High memory threshold
                high_memory_count += 1
        
        # Should have correlation data for analysis
        assert high_latency_count > 0, "No high latency metrics found for correlation analysis"
        
        # Step 5: Engineer exports detailed data for further analysis
        # Request CSV export of the problematic time period
        
        export_params = {
            "agent_id": self.AGENT_ID,
            "start_date": (current_time - timedelta(hours=1)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z"
        }
        
        export_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=export_params
        )
        
        # Should successfully export data as CSV
        assert export_response.status_code == 200
        assert export_response.headers.get("Content-Type") == "text/csv"
        assert "Content-Disposition" in export_response.headers
        
        # Verify CSV contains expected data
        csv_content = export_response.text
        assert "agent_id" in csv_content  # Header present
        assert "latency_ms" in csv_content  # Header present
        assert self.AGENT_ID in csv_content  # Data present
        assert "2500" in csv_content  # Problem latency value present
    
    def test_performance_diagnosis_with_multiple_agents(self):
        """
        Test performance diagnosis workflow with multiple agents.
        Engineer compares performance across agents to isolate issue.
        """
        # This WILL FAIL until both APIs are implemented
        
        current_time = datetime.utcnow()
        agents = [
            "550e8400-e29b-41d4-a716-446655440001",  # Healthy agent
            "550e8400-e29b-41d4-a716-446655440002",  # Problem agent
            "550e8400-e29b-41d4-a716-446655440003"   # Another healthy agent
        ]
        
        # Submit metrics for multiple agents with different performance profiles
        for i, agent_id in enumerate(agents):
            if i == 1:  # Problem agent
                metrics = {
                    "agent_id": agent_id,
                    "timestamp": current_time.isoformat() + "Z",
                    "latency_ms": 3000,  # Much higher latency
                    "cpu_usage_percent": 90,
                    "memory_usage_mb": 9000,
                    "throughput_req_per_min": 8
                }
            else:  # Healthy agents
                metrics = {
                    "agent_id": agent_id,
                    "timestamp": current_time.isoformat() + "Z",
                    "latency_ms": 150,  # Normal latency
                    "cpu_usage_percent": 45,
                    "memory_usage_mb": 2000,
                    "throughput_req_per_min": 50
                }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)  # Allow processing
        
        # Engineer queries all agents to compare performance
        all_agents_response = requests.get(f"{self.DATA_API_BASE}/agents")
        
        assert all_agents_response.status_code == 200
        agents_data = all_agents_response.json()
        assert "agents" in agents_data
        assert len(agents_data["agents"]) >= 3
        
        # Verify problem agent stands out in the comparison
        problem_agent_found = False
        for agent in agents_data["agents"]:
            if agent["agent_id"] == agents[1]:  # Problem agent
                problem_agent_found = True
                # Should show degraded performance indicators
                assert agent.get("status") in ["degraded", "unhealthy", "warning"]
                break
        
        assert problem_agent_found, "Problem agent not properly identified in agents list"
    
    def test_performance_diagnosis_real_time_monitoring(self):
        """
        Test real-time performance monitoring during diagnosis.
        Engineer monitors metrics as they arrive to see live issue progression.
        """
        # This WILL FAIL until real-time capabilities are implemented
        
        current_time = datetime.utcnow()
        agent_id = str(uuid4())
        
        # Submit initial baseline metrics
        baseline_metrics = {
            "agent_id": agent_id,
            "timestamp": (current_time - timedelta(minutes=5)).isoformat() + "Z",
            "latency_ms": 100,
            "cpu_usage_percent": 30,
            "memory_usage_mb": 1500
        }
        
        baseline_response = requests.post(
            f"{self.METRICS_API_BASE}/metrics",
            json=baseline_metrics
        )
        assert baseline_response.status_code == 201
        
        # Submit escalating performance degradation
        for minute_offset in range(4):
            degraded_metrics = {
                "agent_id": agent_id,
                "timestamp": (current_time - timedelta(minutes=4-minute_offset)).isoformat() + "Z",
                "latency_ms": 100 + (minute_offset * 500),  # Escalating latency
                "cpu_usage_percent": 30 + (minute_offset * 15),  # Escalating CPU
                "memory_usage_mb": 1500 + (minute_offset * 1000)  # Escalating memory
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=degraded_metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)  # Allow processing
        
        # Engineer queries recent trend to see degradation pattern
        trend_params = {
            "agent_id": agent_id,
            "start_date": (current_time - timedelta(minutes=6)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "order_by": "timestamp"
        }
        
        trend_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=trend_params
        )
        
        assert trend_response.status_code == 200
        trend_data = trend_response.json()
        assert "metrics" in trend_data
        assert len(trend_data["metrics"]) >= 4
        
        # Verify escalating degradation pattern is detectable
        latencies = [m["latency_ms"] for m in trend_data["metrics"] if "latency_ms" in m]
        latencies.sort()  # Should show increasing trend
        
        # Should be able to detect performance degradation trend
        assert len(latencies) >= 4
        assert latencies[-1] > latencies[0] * 2, "Performance degradation trend not detectable"


@pytest.mark.integration
class TestPerformanceDiagnosisIntegrationEdgeCases:
    """
    Integration tests for edge cases in performance diagnosis workflow.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    
    def test_diagnosis_with_missing_data_points(self):
        """
        Test performance diagnosis when some metrics are missing.
        Engineer should still be able to diagnose with partial data.
        """
        # This WILL FAIL until robust data handling is implemented
        
        current_time = datetime.utcnow()
        agent_id = str(uuid4())
        
        # Submit metrics with some missing fields
        partial_metrics = {
            "agent_id": agent_id,
            "timestamp": current_time.isoformat() + "Z",
            "latency_ms": 5000,
            # Missing cpu_usage_percent
            "memory_usage_mb": 12000
            # Missing throughput_req_per_min
        }
        
        response = requests.post(
            f"{self.METRICS_API_BASE}/metrics",
            json=partial_metrics
        )
        assert response.status_code == 201
        
        time.sleep(1)
        
        # Should still be able to query and analyze available data
        query_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params={
                "agent_id": agent_id,
                "start_date": (current_time - timedelta(minutes=1)).isoformat() + "Z",
                "end_date": current_time.isoformat() + "Z"
            }
        )
        
        assert query_response.status_code == 200
        data = query_response.json()
        assert len(data["metrics"]) > 0
        
        # Should handle missing fields gracefully
        metric = data["metrics"][0]
        assert metric["latency_ms"] == 5000
        assert metric["memory_usage_mb"] == 12000
        # Missing fields should be handled appropriately (null or excluded)
    
    def test_diagnosis_with_concurrent_agents(self):
        """
        Test performance diagnosis with high concurrency.
        Multiple engineers diagnosing different agents simultaneously.
        """
        # This WILL FAIL until concurrent handling is implemented
        
        current_time = datetime.utcnow()
        num_concurrent_agents = 5
        
        # Submit metrics for multiple agents concurrently
        import threading
        import queue
        
        results = queue.Queue()
        
        def submit_agent_metrics(agent_index):
            agent_id = f"concurrent-agent-{agent_index}"
            metrics = {
                "agent_id": agent_id,
                "timestamp": current_time.isoformat() + "Z",
                "latency_ms": 1000 + (agent_index * 100),
                "cpu_usage_percent": 50 + (agent_index * 10),
                "memory_usage_mb": 2000 + (agent_index * 500)
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=metrics
            )
            results.put((agent_index, response.status_code))
        
        # Launch concurrent submissions
        threads = []
        for i in range(num_concurrent_agents):
            thread = threading.Thread(target=submit_agent_metrics, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all submissions
        for thread in threads:
            thread.join()
        
        # Verify all submissions succeeded
        for _ in range(num_concurrent_agents):
            agent_index, status_code = results.get()
            assert status_code == 201, f"Agent {agent_index} submission failed"
        
        time.sleep(2)  # Allow processing
        
        # Verify all agents can be queried independently
        for i in range(num_concurrent_agents):
            agent_id = f"concurrent-agent-{i}"
            
            query_response = requests.get(
                f"{self.DATA_API_BASE}/metrics",
                params={
                    "agent_id": agent_id,
                    "start_date": (current_time - timedelta(minutes=1)).isoformat() + "Z",
                    "end_date": current_time.isoformat() + "Z"
                }
            )
            
            assert query_response.status_code == 200
            data = query_response.json()
            assert len(data["metrics"]) > 0
            assert data["metrics"][0]["agent_id"] == agent_id