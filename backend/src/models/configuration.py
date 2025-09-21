"""
Monitoring Configuration SQLAlchemy model for Sentinel AI.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, CheckConstraint, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class MonitoringConfiguration(BaseModel):
    """Monitoring configuration model for agent monitoring settings."""
    __tablename__ = "monitoring_configuration"
    
    # Primary key
    config_id = Column(UUID(as_uuid=False), primary_key=True, default=BaseModel.generate_uuid)
    
    # Foreign key to AI agent (nullable for global configuration)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("ai_agents.agent_id", ondelete="CASCADE"), nullable=True)
    
    # Configuration settings
    collection_interval_seconds = Column(Integer, nullable=False, default=60)
    retention_days = Column(Integer, nullable=False, default=90)
    alert_thresholds = Column(JSONB, default=dict)
    enabled = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.current_timestamp())
    
    # Relationships
    agent = relationship("AIAgent", back_populates="monitoring_configurations")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("collection_interval_seconds BETWEEN 1 AND 3600", 
                       name="monitoring_config_interval_valid"),
        CheckConstraint("retention_days > 0", name="monitoring_config_retention_positive"),
        # Indexes
        Index("idx_config_agent_enabled", "agent_id", "enabled"),
    )
    
    def __repr__(self):
        return f"<MonitoringConfiguration(config_id='{self.config_id}', agent_id='{self.agent_id}', enabled={self.enabled})>"
    
    def get_alert_threshold(self, metric_name, threshold_type="warning"):
        """Get alert threshold for a specific metric and type."""
        if not self.alert_thresholds:
            return None
        
        metric_thresholds = self.alert_thresholds.get(metric_name, {})
        return metric_thresholds.get(threshold_type)
    
    def set_alert_threshold(self, metric_name, threshold_type, value):
        """Set alert threshold for a specific metric and type."""
        if not self.alert_thresholds:
            self.alert_thresholds = {}
        
        if metric_name not in self.alert_thresholds:
            self.alert_thresholds[metric_name] = {}
        
        self.alert_thresholds[metric_name][threshold_type] = value
        
        # Mark as modified for SQLAlchemy to detect changes
        self.alert_thresholds = dict(self.alert_thresholds)
    
    def is_global_config(self):
        """Check if this is a global configuration (not agent-specific)."""
        return self.agent_id is None