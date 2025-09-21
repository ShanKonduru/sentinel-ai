"""
Unit tests for SQLAlchemy models.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, AIAgent, PerformanceMetric, UserSession, MonitoringConfiguration
from src.models.agent import AgentStatus


class TestModels:
    """Test SQLAlchemy models."""
    
    @pytest.fixture
    def engine(self):
        """Create an in-memory SQLite database for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Create a database session for testing."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_ai_agent_creation(self, session):
        """Test creating an AI agent."""
        agent = AIAgent(
            agent_id=str(uuid4()),
            name="Test Agent",
            description="A test agent",
            status=AgentStatus.RUNNING
        )
        
        session.add(agent)
        session.commit()
        
        # Verify the agent was created
        retrieved_agent = session.query(AIAgent).filter_by(name="Test Agent").first()
        assert retrieved_agent is not None
        assert retrieved_agent.name == "Test Agent"
        assert retrieved_agent.description == "A test agent"
        assert retrieved_agent.status == AgentStatus.RUNNING
        assert retrieved_agent.created_at is not None
    
    def test_performance_metric_creation(self, session):
        """Test creating a performance metric."""
        # First create an agent
        agent = AIAgent(
            agent_id=str(uuid4()),
            name="Test Agent",
            status=AgentStatus.RUNNING
        )
        session.add(agent)
        session.commit()
        
        # Create a metric (use a past timestamp to avoid constraint violations)
        from datetime import timedelta
        past_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        metric = PerformanceMetric(
            metric_id=str(uuid4()),
            agent_id=agent.agent_id,
            timestamp=past_time,
            latency_ms=150.5,
            throughput_req_per_min=60.0,
            cost_per_request=0.001,
            cpu_usage_percent=45.2,
            gpu_usage_percent=70.1,
            memory_usage_mb=512.0
        )
        
        session.add(metric)
        session.commit()
        
        # Verify the metric was created
        retrieved_metric = session.query(PerformanceMetric).filter_by(agent_id=agent.agent_id).first()
        assert retrieved_metric is not None
        assert retrieved_metric.latency_ms == 150.5
        assert retrieved_metric.throughput_req_per_min == 60.0
        assert retrieved_metric.cpu_usage_percent == 45.2
    
    def test_user_session_creation(self, session):
        """Test creating a user session."""
        user_session = UserSession(
            session_id=str(uuid4()),
            user_identifier="user123"
            # Don't set last_activity explicitly - let it use the default
        )
        
        session.add(user_session)
        session.commit()
        
        # Verify the session was created
        retrieved_session = session.query(UserSession).filter_by(user_identifier="user123").first()
        assert retrieved_session is not None
        assert retrieved_session.user_identifier == "user123"
        assert retrieved_session.last_activity is not None
    
    def test_monitoring_configuration_creation(self, session):
        """Test creating a monitoring configuration."""
        config = MonitoringConfiguration(
            config_id=str(uuid4()),
            collection_interval_seconds=60,
            retention_days=90,
            alert_thresholds={
                "latency_ms": 1000,
                "cpu_usage_percent": 80
            }
        )
        
        session.add(config)
        session.commit()
        
        # Verify the configuration was created
        retrieved_config = session.query(MonitoringConfiguration).filter_by(config_id=config.config_id).first()
        assert retrieved_config is not None
        assert retrieved_config.collection_interval_seconds == 60
        assert retrieved_config.retention_days == 90
        assert retrieved_config.alert_thresholds["latency_ms"] == 1000
    
    def test_agent_metrics_relationship(self, session):
        """Test the relationship between agents and metrics."""
        # Create an agent
        agent = AIAgent(
            agent_id=str(uuid4()),
            name="Test Agent",
            status=AgentStatus.RUNNING
        )
        session.add(agent)
        session.commit()
        
        # Create multiple metrics for the agent (use past timestamps)
        from datetime import timedelta
        for i in range(3):
            past_time = datetime.now(timezone.utc) - timedelta(minutes=i+1)
            metric = PerformanceMetric(
                metric_id=str(uuid4()),
                agent_id=agent.agent_id,
                timestamp=past_time,
                latency_ms=100.0 + i * 10
            )
            session.add(metric)
        
        session.commit()
        
        # Verify the relationship
        retrieved_agent = session.query(AIAgent).filter_by(agent_id=agent.agent_id).first()
        assert len(retrieved_agent.performance_metrics) == 3
        
        # Verify metrics are ordered by timestamp descending
        latencies = [metric.latency_ms for metric in retrieved_agent.performance_metrics]
        assert latencies == [120.0, 110.0, 100.0]  # Should be in descending order