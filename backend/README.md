# Sentinel AI Backend

Backend services for the Sentinel AI System providing metrics collection and data retrieval APIs.

## Services

- **Metrics Collection API** (Flask): Receives performance metrics from AI agents
- **Data Retrieval API** (FastAPI): Provides read-only access to metrics data for dashboard
- **Metrics Collector**: Lightweight agent for collecting metrics from AI systems

## Development Setup

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Code formatting
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Run metrics collection API
python -m src.api.metrics_collection.app

# Run data retrieval API  
python -m src.api.data_retrieval.app
```

## Configuration

Environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `METRICS_API_PORT`: Port for metrics collection API (default: 5000)
- `DATA_API_PORT`: Port for data retrieval API (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)