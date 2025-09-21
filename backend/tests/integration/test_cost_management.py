"""
Integration test for Cost Management user scenario.

This test simulates the complete workflow of a team lead analyzing
cost trends across all agents to optimize resource allocation and budget planning.

Based on Journey 2 from quickstart.md - MUST FAIL before implementation.
"""

import pytest
import requests
import time
from datetime import datetime, timedelta
from uuid import uuid4


class TestCostManagementIntegration:
    """
    Integration tests for team lead cost management workflow.
    These tests simulate the complete user journey and MUST fail until implemented.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    
    def test_cost_management_complete_workflow(self):
        """
        Test complete cost management workflow.
        Simulates team lead analyzing costs and identifying optimization opportunities.
        """
        # This WILL FAIL until both APIs are implemented and connected
        
        current_time = datetime.utcnow()
        
        # Step 1: Team lead sets up multiple agents with different cost profiles
        agents_cost_data = [
            {
                "agent_id": "cost-efficient-agent-1",
                "cost_per_request": 0.002,
                "throughput_req_per_min": 100,
                "cpu_usage_percent": 40,
                "memory_usage_mb": 2000
            },
            {
                "agent_id": "expensive-agent-2", 
                "cost_per_request": 0.015,  # 7.5x more expensive
                "throughput_req_per_min": 25,  # Much lower throughput
                "cpu_usage_percent": 80,
                "memory_usage_mb": 8000
            },
            {
                "agent_id": "balanced-agent-3",
                "cost_per_request": 0.005,
                "throughput_req_per_min": 60,
                "cpu_usage_percent": 55,
                "memory_usage_mb": 4000
            },
            {
                "agent_id": "high-volume-agent-4",
                "cost_per_request": 0.003,
                "throughput_req_per_min": 200,
                "cpu_usage_percent": 70,
                "memory_usage_mb": 6000
            }
        ]
        
        # Submit cost metrics for each agent over the past week
        for day_offset in range(7):  # Past week
            for agent_data in agents_cost_data:
                # Add some realistic variation to daily costs
                cost_variation = 1.0 + (day_offset % 3 - 1) * 0.1  # ±10% variation
                
                daily_metrics = {
                    "agent_id": agent_data["agent_id"],
                    "timestamp": (current_time - timedelta(days=day_offset)).isoformat() + "Z",
                    "cost_per_request": agent_data["cost_per_request"] * cost_variation,
                    "throughput_req_per_min": agent_data["throughput_req_per_min"],
                    "cpu_usage_percent": agent_data["cpu_usage_percent"],
                    "memory_usage_mb": agent_data["memory_usage_mb"],
                    "total_requests": agent_data["throughput_req_per_min"] * 60 * 24  # Daily total
                }
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=daily_metrics
                )
                assert response.status_code == 201
        
        time.sleep(3)  # Allow metrics processing
        
        # Step 2: Team lead queries all agents to get cost overview
        agents_response = requests.get(f"{self.DATA_API_BASE}/agents")
        
        assert agents_response.status_code == 200
        agents_data = agents_response.json()
        assert "agents" in agents_data
        assert len(agents_data["agents"]) >= 4
        
        # Verify all test agents are present
        agent_ids = [agent["agent_id"] for agent in agents_data["agents"]]
        for agent_data in agents_cost_data:
            assert agent_data["agent_id"] in agent_ids
        
        # Step 3: Team lead analyzes cost per agent over past week
        week_ago = current_time - timedelta(days=7)
        
        cost_query_params = {
            "start_date": week_ago.isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "metric_types": "cost_per_request,throughput_req_per_min,total_requests",
            "aggregation": "1d"  # Daily aggregation
        }
        
        cost_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=cost_query_params
        )
        
        assert cost_response.status_code == 200
        cost_data = cost_response.json()
        assert "metrics" in cost_data
        assert len(cost_data["metrics"]) > 0
        
        # Step 4: Team lead identifies high-cost agents
        # Calculate cost efficiency for each agent
        agent_cost_efficiency = {}
        
        for metric in cost_data["metrics"]:
            agent_id = metric["agent_id"]
            cost_per_req = metric.get("cost_per_request", 0)
            throughput = metric.get("throughput_req_per_min", 1)
            
            # Cost efficiency = throughput / cost_per_request (higher is better)
            efficiency = throughput / max(cost_per_req, 0.001) if cost_per_req > 0 else 0
            
            if agent_id not in agent_cost_efficiency:
                agent_cost_efficiency[agent_id] = []
            agent_cost_efficiency[agent_id].append(efficiency)
        
        # Calculate average efficiency per agent
        avg_efficiency = {}
        for agent_id, efficiencies in agent_cost_efficiency.items():
            avg_efficiency[agent_id] = sum(efficiencies) / len(efficiencies)
        
        # Should identify expensive-agent-2 as least efficient
        assert "expensive-agent-2" in avg_efficiency
        assert "cost-efficient-agent-1" in avg_efficiency
        
        expensive_agent_efficiency = avg_efficiency["expensive-agent-2"]
        efficient_agent_efficiency = avg_efficiency["cost-efficient-agent-1"]
        
        assert efficient_agent_efficiency > expensive_agent_efficiency * 3, \
            "Cost efficiency difference not properly detectable"
        
        # Step 5: Team lead analyzes cost trends over time
        trend_query_params = {
            "start_date": week_ago.isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "agent_id": "expensive-agent-2",  # Focus on problematic agent
            "metric_types": "cost_per_request",
            "order_by": "timestamp"
        }
        
        trend_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=trend_query_params
        )
        
        assert trend_response.status_code == 200
        trend_data = trend_response.json()
        assert "metrics" in trend_data
        assert len(trend_data["metrics"]) >= 5  # Should have multiple days of data
        
        # Step 6: Team lead exports detailed cost data for budget planning
        export_params = {
            "start_date": week_ago.isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z"
        }
        
        export_response = requests.get(
            f"{self.DATA_API_BASE}/export",
            params=export_params
        )
        
        assert export_response.status_code == 200
        assert export_response.headers.get("Content-Type") == "text/csv"
        
        # Verify CSV contains cost data for analysis
        csv_content = export_response.text
        assert "cost_per_request" in csv_content
        assert "throughput_req_per_min" in csv_content
        assert "expensive-agent-2" in csv_content
        assert "0.015" in csv_content or "0.0165" in csv_content  # High cost value
    
    def test_cost_optimization_analysis(self):
        """
        Test cost optimization analysis workflow.
        Team lead identifies specific optimization opportunities.
        """
        # This WILL FAIL until cost analysis features are implemented
        
        current_time = datetime.utcnow()
        
        # Create agents with different resource utilization patterns
        optimization_agents = [
            {
                "agent_id": "underutilized-expensive",
                "cost_per_request": 0.020,
                "throughput_req_per_min": 10,  # Very low utilization
                "cpu_usage_percent": 20,  # Underutilized
                "memory_usage_mb": 8000  # Over-provisioned
            },
            {
                "agent_id": "overutilized-cheap",
                "cost_per_request": 0.001,
                "throughput_req_per_min": 150,  # High utilization
                "cpu_usage_percent": 95,  # Maxed out
                "memory_usage_mb": 1000  # Under-provisioned
            },
            {
                "agent_id": "optimal-agent",
                "cost_per_request": 0.004,
                "throughput_req_per_min": 80,
                "cpu_usage_percent": 65,  # Well balanced
                "memory_usage_mb": 4000
            }
        ]
        
        # Submit metrics for optimization analysis
        for agent_data in optimization_agents:
            metrics = {
                "agent_id": agent_data["agent_id"],
                "timestamp": current_time.isoformat() + "Z",
                **agent_data
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)
        
        # Query metrics for optimization analysis
        optimization_query = {
            "start_date": (current_time - timedelta(minutes=5)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "metric_types": "cost_per_request,throughput_req_per_min,cpu_usage_percent,memory_usage_mb"
        }
        
        optimization_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=optimization_query
        )
        
        assert optimization_response.status_code == 200
        optimization_data = optimization_response.json()
        assert "metrics" in optimization_data
        
        # Should be able to identify optimization opportunities
        metrics_by_agent = {}
        for metric in optimization_data["metrics"]:
            agent_id = metric["agent_id"]
            metrics_by_agent[agent_id] = metric
        
        # Verify we can detect underutilized expensive resources
        assert "underutilized-expensive" in metrics_by_agent
        underutilized = metrics_by_agent["underutilized-expensive"]
        
        # Should show high cost but low utilization
        assert underutilized["cost_per_request"] >= 0.015
        assert underutilized["throughput_req_per_min"] <= 15
        assert underutilized["cpu_usage_percent"] <= 30
        
        # Should identify this as optimization candidate
        cost_per_throughput = underutilized["cost_per_request"] / max(underutilized["throughput_req_per_min"], 1)
        optimal_metrics = metrics_by_agent["optimal-agent"]
        optimal_cost_per_throughput = optimal_metrics["cost_per_request"] / max(optimal_metrics["throughput_req_per_min"], 1)
        
        assert cost_per_throughput > optimal_cost_per_throughput * 2, \
            "Cost optimization opportunity not detectable"
    
    def test_budget_forecasting_workflow(self):
        """
        Test budget forecasting based on historical cost trends.
        Team lead projects future costs based on current usage patterns.
        """
        # This WILL FAIL until forecasting capabilities are implemented
        
        current_time = datetime.utcnow()
        agent_id = "forecasting-test-agent"
        
        # Submit historical cost data with increasing trend
        for week_offset in range(8):  # 8 weeks of historical data
            weekly_cost = 0.005 + (week_offset * 0.0005)  # Gradually increasing cost
            weekly_throughput = 50 + (week_offset * 2)  # Gradually increasing usage
            
            week_metrics = {
                "agent_id": agent_id,
                "timestamp": (current_time - timedelta(weeks=week_offset)).isoformat() + "Z",
                "cost_per_request": weekly_cost,
                "throughput_req_per_min": weekly_throughput,
                "total_requests": weekly_throughput * 60 * 24 * 7  # Weekly total
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=week_metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)
        
        # Query historical trend for forecasting
        forecast_query = {
            "agent_id": agent_id,
            "start_date": (current_time - timedelta(weeks=8)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "aggregation": "1w",  # Weekly aggregation
            "order_by": "timestamp"
        }
        
        forecast_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=forecast_query
        )
        
        assert forecast_response.status_code == 200
        forecast_data = forecast_response.json()
        assert "metrics" in forecast_data
        assert len(forecast_data["metrics"]) >= 6  # Should have multiple weeks
        
        # Verify trend data suitable for forecasting
        costs = []
        throughputs = []
        
        for metric in sorted(forecast_data["metrics"], key=lambda x: x["timestamp"]):
            if "cost_per_request" in metric:
                costs.append(metric["cost_per_request"])
            if "throughput_req_per_min" in metric:
                throughputs.append(metric["throughput_req_per_min"])
        
        # Should show increasing trend for forecasting
        assert len(costs) >= 6
        assert len(throughputs) >= 6
        
        # Verify increasing cost trend
        assert costs[-1] > costs[0], "Cost trend not suitable for forecasting"
        assert throughputs[-1] > throughputs[0], "Usage trend not suitable for forecasting"
        
        # Calculate simple trend slope
        if len(costs) >= 2:
            cost_slope = (costs[-1] - costs[0]) / len(costs)
            assert cost_slope > 0, "Cost increase trend not detectable for forecasting"


@pytest.mark.integration
class TestCostManagementIntegrationAdvanced:
    """
    Advanced integration tests for cost management scenarios.
    """
    
    METRICS_API_BASE = "http://localhost:5000/api/v1"
    DATA_API_BASE = "http://localhost:8000/api/v1"
    
    def test_multi_team_cost_allocation(self):
        """
        Test cost allocation across multiple teams.
        Organization needs to track costs by team for charge-back.
        """
        # This WILL FAIL until team-based cost tracking is implemented
        
        current_time = datetime.utcnow()
        
        # Define agents belonging to different teams
        team_agents = {
            "ai-research-team": ["research-agent-1", "research-agent-2"],
            "production-team": ["prod-agent-1", "prod-agent-2", "prod-agent-3"],
            "qa-team": ["qa-agent-1"]
        }
        
        team_cost_profiles = {
            "ai-research-team": {"base_cost": 0.010, "usage_factor": 1.5},  # High cost research
            "production-team": {"base_cost": 0.003, "usage_factor": 3.0},   # High volume production
            "qa-team": {"base_cost": 0.005, "usage_factor": 0.8}            # Moderate testing
        }
        
        # Submit metrics for all team agents
        for team, agents in team_agents.items():
            cost_profile = team_cost_profiles[team]
            
            for agent_id in agents:
                team_metrics = {
                    "agent_id": agent_id,
                    "timestamp": current_time.isoformat() + "Z",
                    "cost_per_request": cost_profile["base_cost"],
                    "throughput_req_per_min": 40 * cost_profile["usage_factor"],
                    "team": team  # Team metadata
                }
                
                response = requests.post(
                    f"{self.METRICS_API_BASE}/metrics",
                    json=team_metrics
                )
                assert response.status_code == 201
        
        time.sleep(2)
        
        # Query costs by team for allocation
        team_cost_query = {
            "start_date": (current_time - timedelta(minutes=5)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "group_by": "team",  # Group by team for allocation
            "metric_types": "cost_per_request,throughput_req_per_min"
        }
        
        team_costs_response = requests.get(
            f"{self.DATA_API_BASE}/metrics",
            params=team_cost_query
        )
        
        assert team_costs_response.status_code == 200
        team_costs_data = team_costs_response.json()
        assert "metrics" in team_costs_data
        
        # Should be able to calculate costs per team
        team_totals = {}
        for metric in team_costs_data["metrics"]:
            team = metric.get("team", "unknown")
            cost = metric.get("cost_per_request", 0)
            throughput = metric.get("throughput_req_per_min", 0)
            
            if team not in team_totals:
                team_totals[team] = {"total_cost": 0, "total_throughput": 0}
            
            team_totals[team]["total_cost"] += cost * throughput
            team_totals[team]["total_throughput"] += throughput
        
        # Verify team cost allocation is trackable
        assert "ai-research-team" in team_totals
        assert "production-team" in team_totals
        assert "qa-team" in team_totals
        
        # Production team should have highest total cost due to volume
        prod_total_cost = team_totals["production-team"]["total_cost"]
        research_total_cost = team_totals["ai-research-team"]["total_cost"]
        
        assert prod_total_cost > research_total_cost, \
            "Team cost allocation not properly trackable"
    
    def test_cost_alerting_thresholds(self):
        """
        Test cost alerting when agents exceed budget thresholds.
        Automated detection of cost overruns for proactive management.
        """
        # This WILL FAIL until cost alerting is implemented
        
        current_time = datetime.utcnow()
        
        # Define cost thresholds for different agent types
        cost_thresholds = {
            "budget-agent-low": 0.005,    # Low budget threshold
            "budget-agent-medium": 0.010, # Medium budget threshold
            "budget-agent-high": 0.020    # High budget threshold
        }
        
        # Submit metrics that exceed thresholds
        for agent_id, threshold in cost_thresholds.items():
            # Submit cost that exceeds threshold by 50%
            over_budget_metrics = {
                "agent_id": agent_id,
                "timestamp": current_time.isoformat() + "Z",
                "cost_per_request": threshold * 1.5,  # 50% over budget
                "throughput_req_per_min": 60,
                "budget_threshold": threshold
            }
            
            response = requests.post(
                f"{self.METRICS_API_BASE}/metrics",
                json=over_budget_metrics
            )
            assert response.status_code == 201
        
        time.sleep(2)
        
        # Query for budget threshold violations
        alert_query = {
            "start_date": (current_time - timedelta(minutes=5)).isoformat() + "Z",
            "end_date": current_time.isoformat() + "Z",
            "alert_type": "budget_exceeded"  # Filter for budget alerts
        }
        
        alert_response = requests.get(
            f"{self.DATA_API_BASE}/alerts",  # Alerts endpoint
            params=alert_query
        )
        
        # Should detect budget threshold violations
        assert alert_response.status_code == 200
        alert_data = alert_response.json()
        assert "alerts" in alert_data
        
        # Should have alerts for all over-budget agents
        alert_agent_ids = [alert["agent_id"] for alert in alert_data["alerts"]]
        
        for agent_id in cost_thresholds.keys():
            assert agent_id in alert_agent_ids, \
                f"Budget threshold violation not detected for {agent_id}"