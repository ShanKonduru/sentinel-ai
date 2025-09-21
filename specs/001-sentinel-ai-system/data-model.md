# Data Model: Sentinel AI System

## Core Entities

### AI Agent
**Purpose**: Represents monitored AI agent instances with their metadata and current status
**Attributes**:
- `agent_id` (UUID, Primary Key): Unique identifier for the AI agent
- `name` (String, NOT NULL): Human-readable name for the agent
- `description` (Text): Optional description of the agent's purpose
- `status` (Enum): Current operational status ['running', 'stopped', 'error', 'unknown']
- `created_at` (Timestamp): When the agent was first registered
- `last_seen` (Timestamp): Last time metrics were received from this agent
- `metadata` (JSONB): Flexible storage for agent-specific configuration and properties

**Validation Rules**:
- `agent_id` must be valid UUID format
- `name` must be non-empty and unique per deployment
- `status` must be one of the defined enum values
- `last_seen` cannot be in the future

### Performance Metrics  
**Purpose**: Time-series storage for all collected performance data (immutable records)
**Attributes**:
- `metric_id` (UUID, Primary Key): Unique identifier for this metric record
- `agent_id` (UUID, Foreign Key): Reference to the AI agent
- `timestamp` (Timestamp with timezone): When the metric was collected
- `latency_ms` (Float): Response latency in milliseconds (nullable)
- `throughput_req_per_min` (Float): Requests processed per minute (nullable)
- `cost_per_request` (Float): Cost associated with the request (nullable)
- `cpu_usage_percent` (Float): CPU utilization percentage 0-100 (nullable)
- `gpu_usage_percent` (Float): GPU utilization percentage 0-100 (nullable)
- `memory_usage_mb` (Float): Memory consumption in megabytes (nullable)
- `custom_metrics` (JSONB): Extensible field for additional metrics

**Validation Rules**:
- `agent_id` must reference existing agent
- `timestamp` cannot be in the future
- Percentage values must be between 0 and 100
- At least one metric value must be non-null per record
- `latency_ms` must be positive if provided
- `memory_usage_mb` must be positive if provided

**Relationships**:
- Many-to-One with AI Agent (one agent has many metric records)

### User Session
**Purpose**: Tracks dashboard user interactions and preferences for personalization
**Attributes**:
- `session_id` (UUID, Primary Key): Unique session identifier
- `user_identifier` (String): User identification (email, username, or anonymous ID)
- `created_at` (Timestamp): Session start time
- `last_activity` (Timestamp): Last interaction timestamp
- `preferences` (JSONB): User dashboard preferences (filters, view settings)
- `active_filters` (JSONB): Currently applied filters (agent_id, time_range)

**Validation Rules**:
- `user_identifier` must be non-empty
- `last_activity` must be >= `created_at`
- Session expires after 24 hours of inactivity

### Monitoring Configuration
**Purpose**: System-wide and agent-specific configuration for data collection and thresholds
**Attributes**:
- `config_id` (UUID, Primary Key): Unique configuration identifier
- `agent_id` (UUID, Foreign Key, nullable): Specific agent (null for global config)
- `collection_interval_seconds` (Integer): How often to collect metrics
- `retention_days` (Integer): How long to keep historical data
- `alert_thresholds` (JSONB): Threshold values for alerting
- `enabled` (Boolean): Whether this configuration is active
- `created_at` (Timestamp): When configuration was created
- `updated_at` (Timestamp): Last modification time

**Validation Rules**:
- `collection_interval_seconds` must be between 1 and 3600 (1 hour max)
- `retention_days` must be positive
- If `agent_id` is provided, agent must exist

**Relationships**:
- Many-to-One with AI Agent (optional, for agent-specific config)

## Database Schema Design

### Indexing Strategy
```sql
-- Primary performance index for time-series queries
CREATE INDEX idx_metrics_agent_timestamp ON performance_metrics (agent_id, timestamp DESC);

-- Index for status monitoring queries
CREATE INDEX idx_agents_status ON ai_agents (status) WHERE status != 'running';

-- Index for recent activity
CREATE INDEX idx_agents_last_seen ON ai_agents (last_seen DESC);

-- Index for session management
CREATE INDEX idx_sessions_user_activity ON user_sessions (user_identifier, last_activity DESC);
```

### Partitioning Strategy
```sql
-- Partition performance_metrics by month for better query performance
CREATE TABLE performance_metrics (
    ...
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE performance_metrics_2025_09 PARTITION OF performance_metrics
FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
```

### Data Retention Policy
- **Performance Metrics**: Configurable retention (default 90 days for detailed data)
- **Aggregated Data**: Keep daily/hourly rollups for 1 year
- **Agent Metadata**: Retain indefinitely until manually deleted
- **User Sessions**: Auto-expire after 30 days of inactivity
- **Configuration**: Keep all historical configurations for audit trail

## State Transitions

### AI Agent Status Flow
```
[New] → [running] → [stopped] → [running]
         ↓           ↑
      [error] → [unknown] → [running]
```

**Transition Rules**:
- New agents start in 'unknown' status until first metrics received
- Agents transition to 'running' when metrics are actively received
- Agents transition to 'error' when error metrics are received
- Agents transition to 'unknown' after no metrics for >5 minutes
- Agents transition to 'stopped' when explicitly stopped

### Metrics Collection Flow
```
[Collected] → [Validated] → [Stored] → [Aggregated]
                 ↓              ↓
              [Rejected]   [Indexed]
```

**Business Rules**:
- All metrics records are immutable once stored
- Invalid metrics are logged but not stored
- Aggregations are computed asynchronously
- Historical aggregations are never modified