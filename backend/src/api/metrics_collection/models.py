"""
Pydantic models for Metrics Collection API requests and responses.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
import uuid


class MetricsSubmission(BaseModel):
    """Model for metrics submission request."""
    
    agent_id: str = Field(
        ..., 
        description="Unique identifier for the AI agent",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    timestamp: datetime = Field(
        ...,
        description="When the metrics were collected (ISO 8601)",
        example="2025-09-20T10:30:00Z"
    )
    latency_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Response latency in milliseconds",
        example=150.5
    )
    throughput_req_per_min: Optional[float] = Field(
        None,
        ge=0,
        description="Requests processed per minute",
        example=45.2
    )
    cost_per_request: Optional[float] = Field(
        None,
        ge=0,
        description="Cost associated with the request",
        example=0.002
    )
    cpu_usage_percent: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="CPU utilization percentage",
        example=75.3
    )
    gpu_usage_percent: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="GPU utilization percentage", 
        example=82.1
    )
    memory_usage_mb: Optional[float] = Field(
        None,
        ge=0,
        description="Memory consumption in megabytes",
        example=1024.5
    )
    custom_metrics: Optional[Dict[str, Union[float, str, bool]]] = Field(
        None,
        description="Additional custom metrics as key-value pairs",
        example={"model_tokens": 1500, "cache_hit_rate": 0.85}
    )
    
    @validator('agent_id')
    def validate_agent_id(cls, v):
        """Validate agent_id is a valid UUID string."""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('agent_id must be a valid UUID string')
    
    @validator('timestamp')
    def validate_timestamp_not_future(cls, v):
        """Validate timestamp is not in the future."""
        now = datetime.now(timezone.utc)
        if v.replace(tzinfo=timezone.utc) > now:
            raise ValueError('timestamp cannot be in the future')
        return v
    
    def has_metrics(self) -> bool:
        """Check if submission has any actual metric data."""
        return any([
            self.latency_ms is not None,
            self.throughput_req_per_min is not None,
            self.cost_per_request is not None,
            self.cpu_usage_percent is not None,
            self.gpu_usage_percent is not None,
            self.memory_usage_mb is not None,
            self.custom_metrics and len(self.custom_metrics) > 0
        ])


class SuccessResponse(BaseModel):
    """Model for successful API responses."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(
        ...,
        description="Success message",
        example="Metrics recorded successfully"
    )
    metric_id: str = Field(
        ...,
        description="Unique identifier for the recorded metric",
        example="123e4567-e89b-12d3-a456-426614174000"
    )


class ErrorResponse(BaseModel):
    """Model for error API responses."""
    
    success: bool = Field(False, description="Operation success status")
    error: str = Field(
        ...,
        description="Error message",
        example="Invalid agent_id format"
    )
    code: str = Field(
        ...,
        description="Error code for programmatic handling",
        example="VALIDATION_ERROR"
    )


class HealthResponse(BaseModel):
    """Model for health check response."""
    
    status: str = Field("healthy", description="Service health status")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current timestamp"
    )
    version: str = Field("1.0.0", description="API version")