"""
User Sessions SQLAlchemy model for Sentinel AI.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from .base import BaseModel


class UserSession(BaseModel):
    """User session model for tracking dashboard user sessions and preferences."""
    __tablename__ = "user_sessions"
    
    # Primary key
    session_id = Column(UUID(as_uuid=False), primary_key=True, default=BaseModel.generate_uuid)
    
    # User identification
    user_identifier = Column(String(255), nullable=False)
    
    # Session timing
    last_activity = Column(DateTime(timezone=True), nullable=False, default=func.current_timestamp())
    
    # User preferences and state
    preferences = Column(JSONB, default=dict)
    active_filters = Column(JSONB, default=dict)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(trim(user_identifier)) > 0", name="user_sessions_user_not_empty"),
        CheckConstraint("last_activity >= created_at", name="user_sessions_activity_order"),
        # Indexes
        Index("idx_sessions_user_activity", "user_identifier", "last_activity"),
        Index("idx_sessions_last_activity", "last_activity"),
    )
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', user='{self.user_identifier}', last_activity='{self.last_activity}')>"
    
    def is_active(self, timeout_minutes=30):
        """Check if session is still active based on last activity and timeout."""
        if not self.last_activity:
            return False
        
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        timeout = timedelta(minutes=timeout_minutes)
        
        return (now - self.last_activity) <= timeout
    
    def update_activity(self):
        """Update last activity timestamp to current time."""
        self.last_activity = func.current_timestamp()