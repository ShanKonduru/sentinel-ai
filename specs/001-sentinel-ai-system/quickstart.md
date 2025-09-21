# Quickstart: Sentinel AI System

## System Overview
The Sentinel AI System provides comprehensive monitoring for AI agents through a microservices architecture with real-time data collection, historical analysis, and visual dashboards.

## Quick Setup Guide

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ for development
- Node.js 18+ for frontend development
- PostgreSQL client tools (optional, for database access)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd sentinel_ai
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# DATABASE_URL=postgresql://user:pass@localhost:5432/sentinel_ai
# METRICS_API_PORT=5000
# DATA_API_PORT=8000
# DASHBOARD_PORT=3000
```

### 3. Start All Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Verify Installation
```bash
# Check metrics collection API
curl http://localhost:5000/api/v1/health

# Check data retrieval API  
curl http://localhost:8000/api/v1/health

# Access dashboard
open http://localhost:3000
```

## Core User Journeys

### Journey 1: AI Engineer Diagnosing Performance Issues

**Scenario**: An AI engineer notices their agent is responding slowly and wants to identify the bottleneck.

**Steps**:
1. **Access Dashboard**: Navigate to `http://localhost:3000`
2. **Select Agent**: Choose the problematic agent from the agent list
3. **View Real-time Metrics**: Observe current latency, CPU, and memory usage
4. **Analyze Historical Data**: Switch to historical view to see performance trends
5. **Identify Bottleneck**: Correlate high latency with CPU/memory spikes
6. **Export Data**: Download detailed metrics for further analysis

**Expected Outcome**: Engineer identifies that memory usage spikes correlate with high latency, indicating a memory leak issue.

**Validation**:
```bash
# Send test metrics to simulate performance issue
curl -X POST http://localhost:5000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-09-20T10:30:00Z",
    "latency_ms": 2500,
    "cpu_usage_percent": 95,
    "memory_usage_mb": 8192
  }'

# Verify data appears in dashboard
curl "http://localhost:8000/api/v1/metrics?agent_id=550e8400-e29b-41d4-a716-446655440000"
```

### Journey 2: Team Lead Managing Costs

**Scenario**: A team lead needs to analyze cost trends across all agents to optimize resource allocation and budget planning.

**Steps**:
1. **Access Cost Overview**: Navigate to the cost analysis section of the dashboard
2. **View Cost per Agent**: Review cost breakdown by individual agents
3. **Analyze Trends**: Examine cost patterns over the past month
4. **Identify High-Cost Agents**: Sort agents by cost per request
5. **Resource Optimization**: Identify agents with high costs but low throughput
6. **Generate Report**: Export cost data for budget planning

**Expected Outcome**: Team lead identifies that Agent A has 3x higher cost per request than similar agents, indicating optimization opportunities.

**Validation**:
```bash
# Send cost metrics for multiple agents
for agent in agent1 agent2 agent3; do
  curl -X POST http://localhost:5000/api/v1/metrics \
    -H "Content-Type: application/json" \
    -d '{
      "agent_id": "'$agent'",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
      "cost_per_request": 0.005,
      "throughput_req_per_min": 30
    }'
done

# Query cost data
curl "http://localhost:8000/api/v1/metrics?metric_types=cost_per_request,throughput_req_per_min"
```

### Journey 3: Data Analyst Exporting Historical Data

**Scenario**: A data analyst needs to export 30 days of performance data for a specific agent to run custom analysis in Python.

**Steps**:
1. **Select Time Range**: Choose last 30 days in the dashboard date picker
2. **Filter by Agent**: Select the specific agent of interest
3. **Configure Export**: Choose CSV format with all available metrics
4. **Download Data**: Export the filtered dataset
5. **Validate Data**: Verify exported data completeness and format
6. **Import to Analysis Tool**: Load data into Jupyter notebook for analysis

**Expected Outcome**: Analyst receives complete CSV file with 30 days of metrics data ready for statistical analysis.

**Validation**:
```bash
# Export data for specific agent and date range
curl "http://localhost:8000/api/v1/export?agent_id=550e8400-e29b-41d4-a716-446655440000&start_date=2025-08-20T00:00:00Z&end_date=2025-09-20T23:59:59Z&format=csv" \
  -o agent_metrics.csv

# Verify CSV format
head -5 agent_metrics.csv
wc -l agent_metrics.csv
```

## Integration Test Scenarios

### Test Scenario 1: End-to-End Data Flow
**Purpose**: Verify complete data flow from agent to dashboard
```bash
# 1. Submit metrics
curl -X POST http://localhost:5000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent-123",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "latency_ms": 150,
    "cpu_usage_percent": 45
  }'

# 2. Verify storage
curl "http://localhost:8000/api/v1/metrics?agent_id=test-agent-123&limit=1"

# 3. Check dashboard display (manual verification in browser)
echo "Visit http://localhost:3000 and verify metrics appear"
```

### Test Scenario 2: High Load Simulation
**Purpose**: Verify system handles required 1000+ req/s
```bash
# Install Apache Bench for load testing
# Run high-volume test
ab -n 10000 -c 100 -T 'application/json' -p metrics_payload.json \
  http://localhost:5000/api/v1/metrics

# Verify all requests processed successfully
curl http://localhost:8000/api/v1/metrics | jq '.total'
```

### Test Scenario 3: Failure Recovery
**Purpose**: Verify system gracefully handles service failures
```bash
# 1. Stop database temporarily
docker-compose stop postgres

# 2. Attempt metrics submission (should fail gracefully)
curl -X POST http://localhost:5000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "test", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# 3. Restart database
docker-compose start postgres

# 4. Verify system recovers
curl http://localhost:5000/api/v1/health
curl http://localhost:8000/api/v1/health
```

## Performance Validation

### Metrics Collection API Performance
```bash
# Test response time under load
time curl -X POST http://localhost:5000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "perf-test", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# Expected: < 50ms response time
```

### Dashboard Load Time
```bash
# Measure dashboard load time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000

# Expected: < 3 seconds initial load
```

### Database Query Performance
```bash
# Test large dataset query
time curl "http://localhost:8000/api/v1/metrics?start_date=2025-08-01T00:00:00Z&limit=10000"

# Expected: Reasonable response time for large queries
```

## Troubleshooting Guide

### Common Issues

**Issue**: Metrics not appearing in dashboard
**Solution**: 
1. Check if metrics API is receiving data: `curl http://localhost:5000/api/v1/health`
2. Verify database connection: `docker-compose logs postgres`
3. Check data API: `curl http://localhost:8000/api/v1/metrics`

**Issue**: High memory usage
**Solution**:
1. Monitor container resources: `docker stats`
2. Check database query performance: `docker-compose logs data-api`
3. Review metrics collection frequency in agent configuration

**Issue**: Slow dashboard loading
**Solution**:
1. Check network latency to APIs
2. Verify data aggregation is working properly
3. Consider reducing default time range for initial dashboard load

### Health Check Commands
```bash
# Check all service health
curl http://localhost:5000/api/v1/health  # Metrics API
curl http://localhost:8000/api/v1/health  # Data API
curl http://localhost:3000/health         # Dashboard

# Check database connectivity
docker-compose exec postgres pg_isready

# View service logs
docker-compose logs metrics-api
docker-compose logs data-api
docker-compose logs dashboard
```