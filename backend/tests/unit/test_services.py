"""
Unit tests for data processing services.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal

from src.services import DataAggregationService, CostAnalysisService, PerformanceDiagnosisService
from src.services.aggregation import AggregationInterval
from src.services.cost_analysis import CostPeriod
from src.services.performance_diagnosis import PerformanceIssueType


class TestDataAggregationService:
    """Test data aggregation service."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_session):
        """Create a data aggregation service instance."""
        return DataAggregationService(mock_session)
    
    def test_aggregate_metrics_by_hour(self, service, mock_session):
        """Test metric aggregation by hour."""
        # Mock query result
        mock_result = [
            {
                'time_bucket': datetime(2024, 1, 1, 10, 0, 0),
                'avg_latency': 150.5,
                'avg_throughput': 60.2,
                'avg_cpu': 45.1,
                'avg_memory': 512.0,
                'metric_count': 100
            }
        ]
        mock_session.execute.return_value.fetchall.return_value = mock_result
        
        # Test aggregation
        result = service.aggregate_metrics_by_time(
            agent_id="test-agent",
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2),
            interval=AggregationInterval.HOUR
        )
        
        assert len(result) == 1
        assert result[0]['time_bucket'] == datetime(2024, 1, 1, 10, 0, 0)
        assert result[0]['avg_latency'] == 150.5
        assert result[0]['metric_count'] == 100
    
    def test_get_agent_summary(self, service, mock_session):
        """Test getting agent summary."""
        # Mock the agent query
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent"
        mock_agent.name = "Test Agent"
        mock_agent.status = "running"
        mock_agent.created_at = datetime(2024, 1, 1)
        mock_agent.last_seen = datetime(2024, 1, 1, 12, 0, 0)
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_agent
        
        # Mock the metrics aggregation query
        mock_metrics_result = [(50, 150.5, 60.2, 0.001, 45.1, 512.0)]
        mock_session.execute.return_value.fetchone.return_value = mock_metrics_result[0]
        
        # Test getting summary
        result = service.get_agent_summary("test-agent")
        
        assert result['agent_id'] == "test-agent"
        assert result['name'] == "Test Agent"
        assert result['status'] == "running"
        assert result['total_metrics'] == 50
        assert result['avg_latency_ms'] == 150.5


class TestCostAnalysisService:
    """Test cost analysis service."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_session):
        """Create a cost analysis service instance."""
        return CostAnalysisService(mock_session)
    
    def test_analyze_costs_by_agent(self, service, mock_session):
        """Test cost analysis by agent."""
        # Mock query result
        mock_result = [
            ("agent-1", "Agent 1", Decimal("10.50"), 1000, Decimal("0.0105")),
            ("agent-2", "Agent 2", Decimal("5.25"), 500, Decimal("0.0105"))
        ]
        mock_session.execute.return_value.fetchall.return_value = mock_result
        
        # Test cost analysis
        result = service.analyze_costs_by_agent(
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2)
        )
        
        assert len(result) == 2
        assert result[0]['agent_id'] == "agent-1"
        assert result[0]['total_cost'] == Decimal("10.50")
        assert result[0]['total_requests'] == 1000
        assert result[1]['agent_id'] == "agent-2"
        assert result[1]['total_cost'] == Decimal("5.25")
    
    def test_detect_cost_spikes(self, service, mock_session):
        """Test cost spike detection."""
        # Mock query results for baseline and current period
        mock_baseline = [(Decimal("5.00"),)]  # Previous week average
        mock_current = [
            (datetime(2024, 1, 1), Decimal("15.00")),  # Spike day
            (datetime(2024, 1, 2), Decimal("6.00"))    # Normal day
        ]
        
        mock_session.execute.return_value.fetchone.side_effect = [mock_baseline[0]]
        mock_session.execute.return_value.fetchall.return_value = mock_current
        
        # Test spike detection
        result = service.detect_cost_spikes(
            agent_id="test-agent",
            period=CostPeriod.DAILY,
            spike_threshold=2.0
        )
        
        assert len(result) == 1
        assert result[0]['date'] == datetime(2024, 1, 1)
        assert result[0]['cost'] == Decimal("15.00")
        assert result[0]['baseline_cost'] == Decimal("5.00")
        assert result[0]['spike_ratio'] == 3.0


class TestPerformanceDiagnosisService:
    """Test performance diagnosis service."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_session):
        """Create a performance diagnosis service instance."""
        return PerformanceDiagnosisService(mock_session)
    
    def test_diagnose_performance_issues(self, service, mock_session):
        """Test performance issue diagnosis."""
        # Mock query result with high latency
        mock_result = [
            (1500.0, 30.0, 0.001, 90.0, 85.0, 2048.0, datetime.now()),  # High latency, high CPU
            (200.0, 120.0, 0.001, 45.0, 50.0, 512.0, datetime.now())    # Normal metrics
        ]
        mock_session.execute.return_value.fetchall.return_value = mock_result
        
        # Test diagnosis
        result = service.diagnose_performance_issues("test-agent")
        
        # Should detect high latency and high resource usage
        issue_types = [issue['issue_type'] for issue in result]
        assert PerformanceIssueType.HIGH_LATENCY.value in issue_types
        assert PerformanceIssueType.HIGH_RESOURCE_USAGE.value in issue_types
    
    def test_calculate_performance_score(self, service, mock_session):
        """Test performance score calculation."""
        # Mock metrics for good performance
        mock_result = [
            (150.0, 100.0, 0.001, 45.0, 60.0, 512.0),  # Good metrics
            (180.0, 95.0, 0.001, 50.0, 65.0, 600.0),   # Still good
            (120.0, 110.0, 0.001, 40.0, 55.0, 480.0)   # Very good
        ]
        mock_session.execute.return_value.fetchall.return_value = mock_result
        
        # Test score calculation
        result = service.calculate_performance_score("test-agent")
        
        assert 'overall_score' in result
        assert 'latency_score' in result
        assert 'throughput_score' in result
        assert 'resource_score' in result
        assert 'reliability_score' in result
        
        # Score should be high for good metrics
        assert result['overall_score'] >= 80.0
    
    def test_get_performance_recommendations(self, service, mock_session):
        """Test getting performance recommendations."""
        # Mock recent metrics with performance issues
        mock_metrics = [
            (2000.0, 25.0, 0.005, 95.0, 90.0, 3072.0),  # Multiple issues
        ]
        mock_session.execute.return_value.fetchall.return_value = mock_metrics
        
        # Test recommendations
        result = service.get_performance_recommendations("test-agent")
        
        assert len(result) > 0
        
        # Should have recommendations for high latency and resource usage
        recommendation_types = [rec['category'] for rec in result]
        assert 'latency' in recommendation_types
        assert 'resources' in recommendation_types
        
        # Each recommendation should have required fields
        for rec in result:
            assert 'category' in rec
            assert 'title' in rec
            assert 'description' in rec
            assert 'priority' in rec
            assert 'estimated_impact' in rec