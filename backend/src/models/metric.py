"""
Performance Metrics SQLAlchemy model for Sentinel AI.
"""
from datetime import datetime
from sqlalchemy import Column, Float, CheckConstraint, ForeignKey, Index, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import BaseModel


class PerformanceMetric(BaseModel):
    """Performance metrics model for tracking AI agent performance data."""
    __tablename__ = "performance_metrics"
    
    # Primary key
    metric_id = Column(UUID(as_uuid=False), primary_key=True, default=BaseModel.generate_uuid)
    
    # Foreign key to AI agent
    agent_id = Column(UUID(as_uuid=False), ForeignKey("ai_agents.agent_id", ondelete="CASCADE"), nullable=False)
    
    # Timestamp for the metric (used for partitioning)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.current_timestamp())
    
    # Performance metrics
    latency_ms = Column(Float)
    throughput_req_per_min = Column(Float)
    cost_per_request = Column(Float)
    cpu_usage_percent = Column(Float)
    gpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Custom metrics as JSON
    custom_metrics = Column(JSON, default=dict)
    
    # Relationships
    agent = relationship("AIAgent", back_populates="performance_metrics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("timestamp <= CURRENT_TIMESTAMP", name="performance_metrics_timestamp_not_future"),
        CheckConstraint("latency_ms IS NULL OR latency_ms > 0", name="performance_metrics_latency_positive"),
        CheckConstraint("memory_usage_mb IS NULL OR memory_usage_mb > 0", name="performance_metrics_memory_positive"),
        CheckConstraint("cpu_usage_percent IS NULL OR (cpu_usage_percent >= 0 AND cpu_usage_percent <= 100)", 
                       name="performance_metrics_cpu_percent_valid"),
        CheckConstraint("gpu_usage_percent IS NULL OR (gpu_usage_percent >= 0 AND gpu_usage_percent <= 100)", 
                       name="performance_metrics_gpu_percent_valid"),
        CheckConstraint("""
            latency_ms IS NOT NULL OR 
            throughput_req_per_min IS NOT NULL OR 
            cost_per_request IS NOT NULL OR 
            cpu_usage_percent IS NOT NULL OR 
            gpu_usage_percent IS NOT NULL OR 
            memory_usage_mb IS NOT NULL OR 
            json_array_length(custom_metrics) > 0
        """, name="performance_metrics_at_least_one_metric"),
        # Indexes
        Index("idx_metrics_agent_timestamp", "agent_id", "timestamp"),
        Index("idx_metrics_timestamp", "timestamp"),
        # Table is partitioned by timestamp in the database
        {"postgresql_partition_by": "RANGE (timestamp)"}
    )
    
    def __repr__(self):
        return f"<PerformanceMetric(metric_id='{self.metric_id}', agent_id='{self.agent_id}', timestamp='{self.timestamp}')>"
    
    def has_metrics(self):
        """Check if this metric instance has any actual metric data."""
        return any([
            self.latency_ms is not None,
            self.throughput_req_per_min is not None,
            self.cost_per_request is not None,
            self.cpu_usage_percent is not None,
            self.gpu_usage_percent is not None,
            self.memory_usage_mb is not None,
            self.custom_metrics and len(self.custom_metrics) > 0
        ])