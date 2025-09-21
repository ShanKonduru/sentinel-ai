# Research: Sentinel AI System

## Technology Decisions

### Docker Microservices Deployment
**Decision**: Use Docker Compose for local development and Docker Swarm/Kubernetes for production deployment  
**Rationale**: Docker Compose provides simple multi-container orchestration for development. Docker Swarm offers built-in orchestration for production without additional complexity. Kubernetes as alternative for advanced scaling needs.  
**Alternatives considered**: Bare metal deployment (rejected for lack of isolation), Docker without orchestration (rejected for complexity of multi-service management)

### PostgreSQL High Availability  
**Decision**: PostgreSQL with streaming replication and automated failover using pg_auto_failover or Patroni  
**Rationale**: Streaming replication provides real-time data synchronization. Automated failover ensures minimal downtime. pg_auto_failover offers simpler setup than Patroni for this use case.  
**Alternatives considered**: PostgreSQL clustering with pgpool (rejected for complexity), MongoDB (rejected due to constitution requirement for PostgreSQL), SQLite (rejected for multi-user concurrent access limitations)

### D3.js React Integration
**Decision**: Use React + D3.js with useRef hooks for DOM manipulation and React for component lifecycle management  
**Rationale**: React handles component state and lifecycle, D3 handles complex visualizations and data binding. useRef provides direct DOM access for D3 without conflicting with React's virtual DOM.  
**Alternatives considered**: Pure D3.js (rejected for state management complexity), React-only charting libraries like Recharts (rejected for limited customization), Observable Plot (rejected for integration complexity)

### Lightweight Metrics Collection
**Decision**: Minimal Python agent using async HTTP client (aiohttp) with configurable collection intervals and local buffering  
**Rationale**: Async I/O prevents blocking the monitored application. Local buffering handles network interruptions. Configurable intervals balance data freshness with performance impact.  
**Alternatives considered**: Synchronous HTTP client (rejected for potential blocking), TCP socket streaming (rejected for complexity), File-based collection (rejected for reliability concerns)

### REST API Performance Optimization
**Decision**: FastAPI with async/await, connection pooling, response caching, and horizontal scaling behind load balancer  
**Rationale**: FastAPI's async capabilities handle high concurrency. Connection pooling reduces database overhead. Response caching improves latency. Horizontal scaling meets >1000 req/s requirement.  
**Alternatives considered**: Synchronous Flask (rejected for concurrency limitations), GraphQL (rejected for overhead with simple data model), gRPC (rejected for frontend complexity)

## Implementation Patterns

### Data Collection Pattern
- **Push-based metrics**: Agents actively send data to collection API
- **Batch insertion**: Group multiple metrics for efficient database writes  
- **Circuit breaker**: Agent handles API unavailability gracefully
- **Retry with exponential backoff**: Handles transient failures

### Database Schema Pattern
- **Time-series optimized**: Partitioned tables by time range for query performance
- **Immutable records**: Insert-only pattern as required by constitution
- **Indexing strategy**: Composite indexes on (agent_id, timestamp) for common queries
- **Data retention**: Configurable TTL for old metrics to manage storage

### Dashboard Update Pattern  
- **Real-time updates**: WebSocket connection for live metrics
- **Data aggregation**: Server-side rollups for historical views
- **Progressive loading**: Load recent data first, then historical on demand
- **Client-side caching**: Cache static data (agent metadata) to reduce requests

### Error Handling Pattern
- **Graceful degradation**: Dashboard shows cached data when API unavailable
- **User feedback**: Clear error messages and loading states
- **Monitoring**: Health checks for all services with status endpoints
- **Logging**: Structured logging for debugging and monitoring