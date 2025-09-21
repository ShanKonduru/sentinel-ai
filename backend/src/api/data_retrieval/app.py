"""
FastAPI application for Data Retrieval API.
"""
import csv
import io
from datetime import datetime, timezone
from typing import Optional, List
import logging

from fastapi import FastAPI, HTTPException, Depends, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from sqlalchemy.exc import SQLAlchemyError

from ...database import get_db_session
from ...models import AIAgent, PerformanceMetric, AgentStatus
from .models import (
    Agent, AgentListResponse, Metric, MetricsResponse, TimeRange,
    DataHealthResponse, ErrorResponse, AgentStatusFilter, 
    AggregationLevel, ExportFormat
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sentinel AI Data Retrieval API",
    description="API for retrieving metrics data for dashboard and analysis",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "agents",
            "description": "Agent management operations",
        },
        {
            "name": "metrics",
            "description": "Metrics data retrieval operations",
        },
        {
            "name": "export",
            "description": "Data export operations",
        },
        {
            "name": "health",
            "description": "Health check operations",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/agents",
    response_model=AgentListResponse,
    tags=["agents"],
    summary="List all monitored AI agents",
    description="Retrieve information about all registered AI agents"
)
async def list_agents(
    status: Optional[AgentStatusFilter] = Query(None, description="Filter agents by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip for pagination"),
    db: Session = Depends(get_db_session)
) -> AgentListResponse:
    """List all monitored AI agents with optional filtering and pagination."""
    
    try:
        # Build query
        query = db.query(AIAgent)
        
        # Apply status filter if provided
        if status:
            query = query.filter(AIAgent.status == AgentStatus(status.value))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        agents_db = query.order_by(desc(AIAgent.created_at)).offset(offset).limit(limit).all()
        
        # Convert to response model
        agents = [
            Agent(
                agent_id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                status=agent.status.value,
                created_at=agent.created_at,
                last_seen=agent.last_seen,
                metadata=agent.agent_metadata or {}
            )
            for agent in agents_db
        ]
        
        return AgentListResponse(
            agents=agents,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Failed to retrieve agents",
                "code": "DATABASE_ERROR"
            }
        )


@app.get(
    "/agents/{agent_id}",
    response_model=Agent,
    tags=["agents"],
    summary="Get specific agent details",
    description="Retrieve detailed information about a specific agent"
)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db_session)
) -> Agent:
    """Get detailed information about a specific agent."""
    
    try:
        agent = db.query(AIAgent).filter(AIAgent.agent_id == agent_id).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "code": "AGENT_NOT_FOUND"
                }
            )
        
        return Agent(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            status=agent.status.value,
            created_at=agent.created_at,
            last_seen=agent.last_seen,
            metadata=agent.agent_metadata or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Failed to retrieve agent",
                "code": "DATABASE_ERROR"
            }
        )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    tags=["metrics"],
    summary="Retrieve metrics data",
    description="Get historical and real-time metrics with filtering options"
)
async def get_metrics(
    agent_id: Optional[str] = Query(None, description="Filter metrics for specific agent"),
    start_date: Optional[datetime] = Query(None, description="Start date for time range filter"),
    end_date: Optional[datetime] = Query(None, description="End date for time range filter"),
    metric_types: Optional[str] = Query(None, description="Comma-separated list of metric types to include"),
    aggregation: AggregationLevel = Query(AggregationLevel.RAW, description="Data aggregation level"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(get_db_session)
) -> MetricsResponse:
    """Retrieve metrics data with filtering and aggregation options."""
    
    try:
        # Build query
        query = db.query(PerformanceMetric)
        
        # Apply filters
        filters = []
        
        if agent_id:
            filters.append(PerformanceMetric.agent_id == agent_id)
        
        if start_date:
            filters.append(PerformanceMetric.timestamp >= start_date)
        
        if end_date:
            filters.append(PerformanceMetric.timestamp <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Apply ordering and limit
        metrics_db = query.order_by(desc(PerformanceMetric.timestamp)).limit(limit).all()
        
        # Convert to response model
        metrics = [
            Metric(
                metric_id=metric.metric_id,
                agent_id=metric.agent_id,
                timestamp=metric.timestamp,
                latency_ms=metric.latency_ms,
                throughput_req_per_min=metric.throughput_req_per_min,
                cost_per_request=metric.cost_per_request,
                cpu_usage_percent=metric.cpu_usage_percent,
                gpu_usage_percent=metric.gpu_usage_percent,
                memory_usage_mb=metric.memory_usage_mb,
                custom_metrics=metric.custom_metrics
            )
            for metric in metrics_db
        ]
        
        # Build time range info
        time_range = None
        if start_date or end_date:
            time_range = TimeRange(
                start=start_date or datetime.min.replace(tzinfo=timezone.utc),
                end=end_date or datetime.now(timezone.utc)
            )
        
        return MetricsResponse(
            metrics=metrics,
            total=total,
            aggregation=aggregation.value,
            time_range=time_range
        )
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Failed to retrieve metrics",
                "code": "DATABASE_ERROR"
            }
        )


@app.get(
    "/export",
    tags=["export"],
    summary="Export metrics data",
    description="Export historical metrics data in CSV or JSON format"
)
async def export_metrics(
    agent_id: str = Query(..., description="Agent to export data for"),
    start_date: datetime = Query(..., description="Start date for export"),
    end_date: datetime = Query(..., description="End date for export"),
    format: ExportFormat = Query(ExportFormat.CSV, description="Export format"),
    db: Session = Depends(get_db_session)
):
    """Export metrics data for a specific agent and time range."""
    
    try:
        # Verify agent exists
        agent = db.query(AIAgent).filter(AIAgent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "code": "AGENT_NOT_FOUND"
                }
            )
        
        # Query metrics
        metrics = db.query(PerformanceMetric).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_date,
                PerformanceMetric.timestamp <= end_date
            )
        ).order_by(PerformanceMetric.timestamp).all()
        
        if format == ExportFormat.CSV:
            return _export_csv(metrics, agent.name)
        else:
            # JSON format
            metrics_data = [
                Metric(
                    metric_id=metric.metric_id,
                    agent_id=metric.agent_id,
                    timestamp=metric.timestamp,
                    latency_ms=metric.latency_ms,
                    throughput_req_per_min=metric.throughput_req_per_min,
                    cost_per_request=metric.cost_per_request,
                    cpu_usage_percent=metric.cpu_usage_percent,
                    gpu_usage_percent=metric.gpu_usage_percent,
                    memory_usage_mb=metric.memory_usage_mb,
                    custom_metrics=metric.custom_metrics
                ).dict()
                for metric in metrics
            ]
            
            return MetricsResponse(
                metrics=metrics_data,
                total=len(metrics),
                aggregation="raw",
                time_range=TimeRange(start=start_date, end=end_date)
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Failed to export metrics",
                "code": "EXPORT_ERROR"
            }
        )


def _export_csv(metrics: List[PerformanceMetric], agent_name: str) -> StreamingResponse:
    """Generate CSV export response."""
    
    def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'metric_id', 'agent_id', 'timestamp', 'latency_ms', 
            'throughput_req_per_min', 'cost_per_request', 'cpu_usage_percent',
            'gpu_usage_percent', 'memory_usage_mb', 'custom_metrics'
        ])
        
        # Write data rows
        for metric in metrics:
            writer.writerow([
                metric.metric_id,
                metric.agent_id,
                metric.timestamp.isoformat(),
                metric.latency_ms,
                metric.throughput_req_per_min,
                metric.cost_per_request,
                metric.cpu_usage_percent,
                metric.gpu_usage_percent,
                metric.memory_usage_mb,
                str(metric.custom_metrics) if metric.custom_metrics else ""
            ])
            
            # Yield the buffer content and reset
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
    
    filename = f"metrics_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get(
    "/health",
    response_model=DataHealthResponse,
    tags=["health"],
    summary="Health check endpoint",
    description="Check if the data retrieval service is healthy"
)
async def health_check(db: Session = Depends(get_db_session)) -> DataHealthResponse:
    """Health check endpoint to verify service and database status."""
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        database_status = "connected"
        
        return DataHealthResponse(
            status="healthy",
            database_status=database_status,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "error": "Service unhealthy - database connection failed",
                "code": "SERVICE_UNHEALTHY"
            }
        )


# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Data Retrieval API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Data Retrieval API shutting down...")
    
    try:
        from ...database import close_database
        close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.src.api.data_retrieval.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )