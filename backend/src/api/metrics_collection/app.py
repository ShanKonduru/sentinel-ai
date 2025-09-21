"""
FastAPI application for Metrics Collection API.
"""
from datetime import datetime, timezone
from typing import Dict, Any
import logging

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ...database import get_db_session
from ...models import AIAgent, PerformanceMetric, AgentStatus
from .models import MetricsSubmission, SuccessResponse, ErrorResponse, HealthResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sentinel AI Metrics Collection API",
    description="API for collecting performance metrics from AI agents",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "metrics",
            "description": "Metrics collection operations",
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


@app.post(
    "/metrics",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["metrics"],
    summary="Submit metrics data from AI agent",
    description="Endpoint for AI agents to submit their performance metrics"
)
async def submit_metrics(
    metrics: MetricsSubmission,
    db: Session = Depends(get_db_session)
) -> SuccessResponse:
    """Submit performance metrics from an AI agent."""
    
    try:
        # Validate that the submission has at least one metric
        if not metrics.has_metrics():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "At least one metric value must be provided",
                    "code": "NO_METRICS_PROVIDED"
                }
            )
        
        # Check if agent exists, create if it doesn't
        agent = db.query(AIAgent).filter(AIAgent.agent_id == metrics.agent_id).first()
        if not agent:
            # Create new agent with minimal information
            agent = AIAgent(
                agent_id=metrics.agent_id,
                name=f"Agent-{metrics.agent_id[:8]}",  # Use first 8 chars of UUID
                description="Auto-created from metrics submission",
                status=AgentStatus.RUNNING
            )
            db.add(agent)
            db.flush()  # Get the agent ID without committing
            logger.info(f"Created new agent: {agent.agent_id}")
        
        # Update agent's last_seen timestamp
        agent.last_seen = metrics.timestamp
        agent.status = AgentStatus.RUNNING  # Agent is submitting metrics, so it's running
        
        # Create performance metric record
        performance_metric = PerformanceMetric(
            agent_id=metrics.agent_id,
            timestamp=metrics.timestamp,
            latency_ms=metrics.latency_ms,
            throughput_req_per_min=metrics.throughput_req_per_min,
            cost_per_request=metrics.cost_per_request,
            cpu_usage_percent=metrics.cpu_usage_percent,
            gpu_usage_percent=metrics.gpu_usage_percent,
            memory_usage_mb=metrics.memory_usage_mb,
            custom_metrics=metrics.custom_metrics or {}
        )
        
        db.add(performance_metric)
        db.commit()
        
        logger.info(f"Recorded metrics for agent {metrics.agent_id}, metric_id: {performance_metric.metric_id}")
        
        return SuccessResponse(
            message="Metrics recorded successfully",
            metric_id=performance_metric.metric_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while recording metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Database error occurred",
                "code": "DATABASE_ERROR"
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while recording metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "code": "INTERNAL_ERROR"
            }
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check endpoint",
    description="Check if the metrics collection service is healthy"
)
async def health_check(db: Session = Depends(get_db_session)) -> HealthResponse:
    """Health check endpoint to verify service status."""
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0"
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


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """Custom handler for validation errors."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "success": False,
            "error": "Validation error",
            "code": "VALIDATION_ERROR",
            "details": exc.detail if hasattr(exc, 'detail') else str(exc)
        }
    )


# Add startup event to initialize database if needed
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Metrics Collection API starting up...")
    
    try:
        # Test database connection
        from ...database import get_database_manager
        db_manager = get_database_manager()
        if db_manager.test_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed during startup")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Metrics Collection API shutting down...")
    
    try:
        from ...database import close_database
        close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.src.api.metrics_collection.app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )