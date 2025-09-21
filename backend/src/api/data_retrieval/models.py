"""
Pydantic models for Data Retrieval API requests and responses.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class AgentStatusFilter(str, Enum):
    """Enum for agent status filtering."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class AggregationLevel(str, Enum):
    """Enum for metric aggregation levels."""
    RAW = "raw"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


class ExportFormat(str, Enum):
    """Enum for export formats."""
    CSV = "csv"
    JSON = "json"


class Agent(BaseModel):
    """Model for agent information."""
    
    agent_id: str = Field(
        ...,
        description="Unique identifier for the agent",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    name: str = Field(
        ...,
        description="Agent name",
        example="GPT-4 Chat Agent"
    )
    description: Optional[str] = Field(
        None,
        description="Agent description",
        example="Customer service chat agent using GPT-4"
    )
    status: str = Field(
        ...,
        description="Current agent status",
        example="running"
    )
    created_at: datetime = Field(
        ...,
        description="When the agent was created",
        example="2025-09-15T08:00:00Z"
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="When the agent was last seen",
        example="2025-09-20T10:29:45Z"
    )
    agent_metadata: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata",
        description="Agent metadata",
        example={
            "model": "gpt-4",
            "version": "1.2.3",
            "deployment": "production"
        }
    )


class AgentListResponse(BaseModel):
    """Response model for agent list endpoint."""
    
    agents: List[Agent] = Field(
        ...,
        description="List of agents"
    )
    total: int = Field(
        ...,
        description="Total number of agents (for pagination)",
        example=25
    )
    limit: int = Field(
        ...,
        description="Applied limit",
        example=50
    )
    offset: int = Field(
        ...,
        description="Applied offset",
        example=0
    )


class Metric(BaseModel):
    """Model for metric data."""
    
    metric_id: str = Field(
        ...,
        description="Unique identifier for the metric"
    )
    agent_id: str = Field(
        ...,
        description="Agent that generated this metric"
    )
    timestamp: datetime = Field(
        ...,
        description="When the metric was recorded"
    )
    latency_ms: Optional[float] = Field(
        None,
        description="Response latency in milliseconds"
    )
    throughput_req_per_min: Optional[float] = Field(
        None,
        description="Requests processed per minute"
    )
    cost_per_request: Optional[float] = Field(
        None,
        description="Cost per request"
    )
    cpu_usage_percent: Optional[float] = Field(
        None,
        description="CPU usage percentage"
    )
    gpu_usage_percent: Optional[float] = Field(
        None,
        description="GPU usage percentage"
    )
    memory_usage_mb: Optional[float] = Field(
        None,
        description="Memory usage in megabytes"
    )
    custom_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom metrics data"
    )


class TimeRange(BaseModel):
    """Model for time range information."""
    
    start: datetime = Field(
        ...,
        description="Start of time range"
    )
    end: datetime = Field(
        ...,
        description="End of time range"
    )


class MetricsResponse(BaseModel):
    """Response model for metrics data."""
    
    metrics: List[Metric] = Field(
        ...,
        description="List of metrics"
    )
    total: int = Field(
        ...,
        description="Total number of metrics matching query"
    )
    aggregation: str = Field(
        ...,
        description="Applied aggregation level",
        example="hour"
    )
    time_range: Optional[TimeRange] = Field(
        None,
        description="Applied time range filter"
    )


class DataHealthResponse(BaseModel):
    """Response model for data API health check."""
    
    status: str = Field(
        "healthy",
        description="Service health status"
    )
    database_status: str = Field(
        ...,
        description="Database connection status",
        example="connected"
    )
    timestamp: datetime = Field(
        ...,
        description="Current timestamp"
    )


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    success: bool = Field(
        False,
        description="Operation success status"
    )
    error: str = Field(
        ...,
        description="Error message"
    )
    code: str = Field(
        ...,
        description="Error code for programmatic handling"
    )