"""
AI Agents SQLAlchemy model for Sentinel AI.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, DateTime, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import BaseModel


class AgentStatus(enum.Enum):
    """Enumeration for agent status values."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class AIAgent(BaseModel):
    """AI Agent model representing monitored AI agents in the system."""
    __tablename__ = "ai_agents"
    
    # Primary key
    agent_id = Column(UUID(as_uuid=False), primary_key=True, default=BaseModel.generate_uuid)
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    status = Column(Enum(AgentStatus), nullable=False, default=AgentStatus.UNKNOWN)
    
    # Timestamps
    last_seen = Column(DateTime(timezone=True))
    
    # Agent metadata 
    agent_metadata = Column(JSON, default=dict)
    
    # Relationships
    performance_metrics = relationship(
        "PerformanceMetric", 
        back_populates="agent", 
        cascade="all, delete-orphan"
    )
    monitoring_configurations = relationship(
        "MonitoringConfiguration", 
        back_populates="agent", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ai_agents_name_not_empty"),
        CheckConstraint("last_seen <= CURRENT_TIMESTAMP", name="ai_agents_last_seen_not_future"),
    )
    
    def __repr__(self):
        return f"<AIAgent(agent_id='{self.agent_id}', name='{self.name}', status='{self.status.value}')>"
    
    def to_dict(self):
        """Convert agent to dictionary including computed fields."""
        base_dict = super().to_dict()
        base_dict["status"] = self.status.value if self.status else None
        return base_dict