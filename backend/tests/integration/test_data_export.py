"""
Integration test for Data Export Workflow user scenario.

This test simulates the complete workflow of a data analyst exporting
historical data for custom analysis in external tools like Python/Jupyter.

Based on Journey 3 from quickstart.md - MUST FAIL before implementation.
"""

import pytest
import requests
import time
import csv
import io
from datetime import datetime, timedelta
from uuid import uuid4


class TestDataExportWorkflowIntegration:
    """
    Integration tests for data analyst export workflow.
    These tests simulate the complete user journey and MUST fail until implemented.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    
    def test_data_export_complete_workflow(self):
        """
        Test complete data export workflow.
        Simulates data analyst exporting 30 days of performance data for analysis.
        """
        # This WILL FAIL until both APIs are implemented and connected
        
        current_time = datetime.utcnow()
        agent_id = "analysis-target-agent"
        
        # Step 1: Data analyst identifies target agent and time range
        # Simulate 30 days of comprehensive metrics data
        
        metrics_data = []
        for day_offset in range(30):
            # Generate multiple metrics per day to simulate realistic data volume
            for hour in range(0, 24, 4):  # Every 4 hours
                timestamp = current_time - timedelta(days=day_offset, hours=hour)
                
                # Simulate realistic performance patterns
                # - Higher latency during peak hours
                # - Memory usage that gradually increases over time
                # - CPU usage with daily cycles
                
                peak_factor = 1.5 if 8 <= hour <= 18 else 1.0  # Business hours peak
                drift_factor = 1.0 + (day_offset * 0.01)  # Gradual memory drift
                
                daily_metrics = {
                    "agent_id": agent_id,
                    "timestamp": timestamp.isoformat() + "Z",
                    "latency_ms": int(100 + (hour * 5) * peak_factor),
                    "cpu_usage_percent": int(30 + (hour % 12) * 3),
                    "memory_usage_mb": int(2000 * drift_factor + (hour * 50)),
                    "throughput_req_per_min": int(50 * peak_factor),
                    "cost_per_request": 0.005 + (day_offset * 0.0001),  # Gradual cost increase
                    "error_rate_percent": max(0, int((hour - 12) * 0.1)),  # Higher errors mid-day
                    "response_size_bytes": 1024 + (hour * 100)
                }
                
                metrics_data.append(daily_metrics)
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=daily_metrics
                )
                assert response.status_code == 201
        
        time.sleep(5)  # Allow comprehensive data processing
        
        # Step 2: Data analyst validates data availability before export
        # Query to confirm all 30 days of data are available
        
        thirty_days_ago = current_time - timedelta(days=30)
        
        validation_query = {
            "agent_id": agent_id,
            "start_date": thirty_days_ago.isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "limit": 10  # Just check for presence, not full dataset
        }
        
        validation_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=validation_query
        )
        
        assert validation_response.status_code == 200
        validation_data = validation_response.json()
        assert "metrics" in validation_data
        assert len(validation_data["metrics"]) > 0, "No historical data available for export"
        
        # Step 3: Data analyst configures and requests comprehensive export
        # Export all 30 days of data in CSV format
        
        export_params = {
            "agent_id": agent_id,
            "start_date": thirty_days_ago.isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "format": "csv"  # Explicit CSV format request
        }
        
        export_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=export_params
        )
        
        # Should successfully export comprehensive dataset
        assert export_response.status_code == 200
        assert export_response.headers.get("Content-Type") == "text/csv"
        assert "Content-Disposition" in export_response.headers
        assert "attachment" in export_response.headers["Content-Disposition"]
        assert ".csv" in export_response.headers["Content-Disposition"]
        
        # Step 4: Data analyst validates exported CSV structure and content
        csv_content = export_response.text
        
        # Parse CSV to validate structure
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        csv_rows = list(csv_reader)
        
        # Should have substantial dataset
        assert len(csv_rows) >= 150, f"Expected ~180 records (30 days * 6 per day), got {len(csv_rows)}"
        
        # Validate CSV headers contain all expected metrics
        expected_headers = [
            "agent_id", "timestamp", "latency_ms", "cpu_usage_percent", 
            "memory_usage_mb", "throughput_req_per_min", "cost_per_request",
            "error_rate_percent", "response_size_bytes"
        ]
        
        csv_headers = csv_reader.fieldnames
        for header in expected_headers:
            assert header in csv_headers, f"Expected header '{header}' missing from CSV"
        
        # Validate data consistency
        for row in csv_rows:
            assert row["agent_id"] == agent_id
            assert row["timestamp"]  # Should have timestamp
            assert float(row["latency_ms"]) > 0
            assert 0 <= float(row["cpu_usage_percent"]) <= 100
            assert float(row["memory_usage_mb"]) > 0
        
        # Step 5: Data analyst validates time range coverage
        # Extract timestamps to verify 30-day coverage
        
        timestamps = [datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")) for row in csv_rows]
        timestamps.sort()
        
        earliest_timestamp = timestamps[0]
        latest_timestamp = timestamps[-1]
        
        # Should cover approximately 30 days
        time_span = latest_timestamp - earliest_timestamp
        assert time_span.days >= 28, f"Time span only {time_span.days} days, expected ~30"
        
        # Step 6: Data analyst validates data quality for analysis
        # Check for reasonable data patterns that would support analysis
        
        latencies = [float(row["latency_ms"]) for row in csv_rows]
        memory_usage = [float(row["memory_usage_mb"]) for row in csv_rows]
        costs = [float(row["cost_per_request"]) for row in csv_rows]
        
        # Should have realistic ranges
        assert min(latencies) >= 50, "Unrealistic low latency values"
        assert max(latencies) <= 500, "Unrealistic high latency values"
        assert min(memory_usage) >= 1000, "Unrealistic low memory usage"
        assert len(set(costs)) > 1, "Cost data should show variation over time"
        
        # Should show expected patterns (memory drift, cost increase)
        early_memory = sum(memory_usage[:20]) / 20  # First 20 records
        late_memory = sum(memory_usage[-20:]) / 20  # Last 20 records
        assert late_memory > early_memory, "Expected memory usage drift not present"
        
        early_cost = sum(costs[:20]) / 20
        late_cost = sum(costs[-20:]) / 20
        assert late_cost > early_cost, "Expected cost increase trend not present"
    
    def test_filtered_export_workflow(self):
        """
        Test data export workflow with filtering and aggregation.
        Data analyst exports specific subsets of data for focused analysis.
        """
        # This WILL FAIL until filtering and aggregation are implemented
        
        current_time = datetime.utcnow()
        agent_id = "filtered-export-agent"
        
        # Create diverse data for filtering tests
        for day_offset in range(7):  # One week of data
            for metric_type in ["normal", "high_latency", "high_error"]:
                timestamp = current_time - timedelta(days=day_offset, hours=day_offset*2)
                
                if metric_type == "normal":
                    metrics = {
                        "agent_id": agent_id,
                        "timestamp": timestamp.isoformat() + "Z",
                        "latency_ms": 150,
                        "cpu_usage_percent": 50,
                        "memory_usage_mb": 3000,
                        "error_rate_percent": 1
                    }
                elif metric_type == "high_latency":
                    metrics = {
                        "agent_id": agent_id,
                        "timestamp": (timestamp + timedelta(hours=1)).isoformat() + "Z",
                        "latency_ms": 2000,  # High latency
                        "cpu_usage_percent": 80,
                        "memory_usage_mb": 5000,
                        "error_rate_percent": 2
                    }
                else:  # high_error
                    metrics = {
                        "agent_id": agent_id,
                        "timestamp": (timestamp + timedelta(hours=2)).isoformat() + "Z",
                        "latency_ms": 300,
                        "cpu_usage_percent": 60,
                        "memory_usage_mb": 3500,
                        "error_rate_percent": 15  # High error rate
                    }
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=metrics
                )
                assert response.status_code == 201
        
        time.sleep(3)
        
        # Export with latency filter
        high_latency_export_params = {
            "agent_id": agent_id,
            "start_date": (current_time - timedelta(days=7)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "filter": "latency_ms>1000",  # Filter for high latency only
            "format": "csv"
        }
        
        high_latency_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=high_latency_export_params
        )
        
        assert high_latency_response.status_code == 200
        filtered_csv = high_latency_response.text
        
        # Validate filtering worked
        filtered_reader = csv.DictReader(io.StringIO(filtered_csv))
        filtered_rows = list(filtered_reader)
        
        assert len(filtered_rows) > 0, "No high latency records found"
        
        # All records should have high latency
        for row in filtered_rows:
            assert float(row["latency_ms"]) > 1000, "Filter did not work properly"
        
        # Export with aggregation
        aggregated_export_params = {
            "agent_id": agent_id,
            "start_date": (current_time - timedelta(days=7)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "aggregation": "1d",  # Daily aggregation
            "format": "csv"
        }
        
        aggregated_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=aggregated_export_params
        )
        
        assert aggregated_response.status_code == 200
        aggregated_csv = aggregated_response.text
        
        # Validate aggregation
        aggregated_reader = csv.DictReader(io.StringIO(aggregated_csv))
        aggregated_rows = list(aggregated_reader)
        
        # Should have fewer rows due to aggregation (max 7 for daily over 7 days)
        assert len(aggregated_rows) <= 7, "Aggregation did not reduce data points"
        assert len(aggregated_rows) > 0, "Aggregation produced no results"
    
    def test_large_dataset_export_performance(self):
        """
        Test data export performance with large datasets.
        Ensures export can handle realistic data volumes efficiently.
        """
        # This WILL FAIL until performance optimization is implemented
        
        current_time = datetime.utcnow()
        agent_id = "large-dataset-agent"
        
        # Create large dataset (simulate high-frequency monitoring)
        total_records = 0
        batch_size = 100
        
        # Submit data in batches to simulate realistic high-volume scenario
        for batch in range(5):  # 5 batches
            batch_start_time = time.time()
            
            for record in range(batch_size):
                timestamp = current_time - timedelta(days=1, minutes=record + (batch * batch_size))
                
                large_dataset_metrics = {
                    "agent_id": agent_id,
                    "timestamp": timestamp.isoformat() + "Z",
                    "latency_ms": 100 + (record % 50),
                    "cpu_usage_percent": 40 + (record % 30),
                    "memory_usage_mb": 2000 + (record * 10),
                    "throughput_req_per_min": 50 + (record % 20),
                    "cost_per_request": 0.005,
                    "request_id": f"req_{batch}_{record}",  # Additional data
                    "user_agent": f"client_type_{record % 5}",
                    "response_size_bytes": 1024 + (record * 100)
                }
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=large_dataset_metrics
                )
                assert response.status_code == 201
                total_records += 1
            
            batch_time = time.time() - batch_start_time
            # Should process batches efficiently
            assert batch_time < 30, f"Batch {batch} took {batch_time:.2f}s, too slow for large datasets"
        
        time.sleep(5)  # Allow processing
        
        # Test large export performance
        large_export_start = time.time()
        
        large_export_params = {
            "agent_id": agent_id,
            "start_date": (current_time - timedelta(days=2)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "format": "csv"
        }
        
        large_export_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=large_export_params,
            timeout=60  # Allow more time for large export
        )
        
        large_export_time = time.time() - large_export_start
        
        # Should handle large export efficiently
        assert large_export_response.status_code == 200
        assert large_export_time < 30, f"Large export took {large_export_time:.2f}s, too slow"
        
        # Validate large dataset integrity
        large_csv_content = large_export_response.text
        large_csv_reader = csv.DictReader(io.StringIO(large_csv_content))
        large_csv_rows = list(large_csv_reader)
        
        # Should have most of the submitted records
        assert len(large_csv_rows) >= total_records * 0.9, \
            f"Expected ~{total_records} records, got {len(large_csv_rows)}"
        
        # Validate data integrity in large export
        request_ids = [row.get("request_id", "") for row in large_csv_rows if row.get("request_id")]
        assert len(set(request_ids)) >= 400, "Request ID uniqueness not maintained in large export"


@pytest.mark.integration
class TestDataExportWorkflowAdvanced:
    """
    Advanced integration tests for data export scenarios.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    
    def test_multi_agent_comparative_export(self):
        """
        Test export workflow for comparative analysis across multiple agents.
        Data analyst exports data for A/B testing or performance comparison.
        """
        # This WILL FAIL until multi-agent export is implemented
        
        current_time = datetime.utcnow()
        
        # Create comparative dataset
        agents = ["control-agent", "variant-a-agent", "variant-b-agent"]
        performance_profiles = {
            "control-agent": {"latency_base": 200, "cpu_base": 50},
            "variant-a-agent": {"latency_base": 150, "cpu_base": 60},  # Faster but more CPU
            "variant-b-agent": {"latency_base": 250, "cpu_base": 40}   # Slower but less CPU
        }
        
        for agent_id in agents:
            profile = performance_profiles[agent_id]
            
            for hour_offset in range(24):  # 24 hours of comparative data
                timestamp = current_time - timedelta(hours=hour_offset)
                
                comparative_metrics = {
                    "agent_id": agent_id,
                    "timestamp": timestamp.isoformat() + "Z",
                    "latency_ms": profile["latency_base"] + (hour_offset % 10),
                    "cpu_usage_percent": profile["cpu_base"] + (hour_offset % 15),
                    "memory_usage_mb": 3000 + (hour_offset * 50),
                    "throughput_req_per_min": 60 - (hour_offset % 20),
                    "cost_per_request": 0.005
                }
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=comparative_metrics
                )
                assert response.status_code == 201
        
        time.sleep(3)
        
        # Export comparative dataset
        multi_agent_export_params = {
            "agent_ids": ",".join(agents),  # Multiple agents
            "start_date": (current_time - timedelta(hours=24)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "format": "csv",
            "include_agent_metadata": "true"
        }
        
        multi_agent_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=multi_agent_export_params
        )
        
        assert multi_agent_response.status_code == 200
        comparative_csv = multi_agent_response.text
        
        # Validate comparative data structure
        comparative_reader = csv.DictReader(io.StringIO(comparative_csv))
        comparative_rows = list(comparative_reader)
        
        # Should have data for all agents
        agent_ids_in_export = set(row["agent_id"] for row in comparative_rows)
        for agent_id in agents:
            assert agent_id in agent_ids_in_export, f"Agent {agent_id} missing from comparative export"
        
        # Should be suitable for comparative analysis
        assert len(comparative_rows) >= len(agents) * 20, "Insufficient data for comparative analysis"
        
        # Validate performance differences are preserved
        agent_avg_latencies = {}
        for row in comparative_rows:
            agent_id = row["agent_id"]
            latency = float(row["latency_ms"])
            
            if agent_id not in agent_avg_latencies:
                agent_avg_latencies[agent_id] = []
            agent_avg_latencies[agent_id].append(latency)
        
        # Calculate averages
        for agent_id, latencies in agent_avg_latencies.items():
            agent_avg_latencies[agent_id] = sum(latencies) / len(latencies)
        
        # Should preserve performance characteristics
        assert agent_avg_latencies["variant-a-agent"] < agent_avg_latencies["control-agent"]
        assert agent_avg_latencies["variant-b-agent"] > agent_avg_latencies["control-agent"]
    
    def test_scheduled_export_workflow(self):
        """
        Test scheduled/automated export workflow.
        Data analyst sets up recurring exports for ongoing analysis.
        """
        # This WILL FAIL until scheduled export capabilities are implemented
        
        current_time = datetime.utcnow()
        agent_id = "scheduled-export-agent"
        
        # Create data for scheduled export
        for day_offset in range(3):  # 3 days of data
            daily_metrics = {
                "agent_id": agent_id,
                "timestamp": (current_time - timedelta(days=day_offset)).isoformat() + "Z",
                "latency_ms": 180 + (day_offset * 20),
                "cpu_usage_percent": 55 + (day_offset * 5),
                "memory_usage_mb": 3200 + (day_offset * 100),
                "daily_summary": True  # Marker for daily aggregation
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=daily_metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)
        
        # Test scheduled export configuration
        schedule_config = {
            "agent_id": agent_id,
            "export_frequency": "daily",
            "export_format": "csv",
            "export_time": "23:59",
            "retention_days": 30,
            "email_recipients": ["analyst@company.com"]
        }
        
        schedule_response = requests.post(
            f"{self.DATA_API_BASE}/export/schedule",
            json=schedule_config
        )
        
        # Should successfully configure scheduled export
        assert schedule_response.status_code == 201
        schedule_result = schedule_response.json()
        assert "schedule_id" in schedule_result
        assert schedule_result["status"] == "scheduled"
        
        # Test manual trigger of scheduled export
        manual_trigger_params = {
            "schedule_id": schedule_result["schedule_id"],
            "trigger_reason": "manual_test"
        }
        
        trigger_response = requests.post(
            f"{self.DATA_API_BASE}/export/trigger",
            json=manual_trigger_params
        )
        
        assert trigger_response.status_code == 200
        trigger_result = trigger_response.json()
        assert "export_job_id" in trigger_result
        
        # Should be able to check export job status
        job_status_response = requests.get(
            f"{self.DATA_API_BASE}/export/jobs/{trigger_result['export_job_id']}"
        )
        
        assert job_status_response.status_code == 200
        job_status = job_status_response.json()
        assert "status" in job_status
        assert job_status["status"] in ["pending", "running", "completed", "failed"]