-- Sentinel AI Database Schema
-- Version: 1.0.0
-- Created: 2025-01-09

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE agent_status AS ENUM ('running', 'stopped', 'error', 'unknown');

-- AI Agents table
CREATE TABLE ai_agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status agent_status NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT ai_agents_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT ai_agents_last_seen_not_future CHECK (last_seen <= CURRENT_TIMESTAMP)
);

-- Performance Metrics table (partitioned by timestamp)
CREATE TABLE performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    latency_ms DOUBLE PRECISION,
    throughput_req_per_min DOUBLE PRECISION,
    cost_per_request DOUBLE PRECISION,
    cpu_usage_percent DOUBLE PRECISION,
    gpu_usage_percent DOUBLE PRECISION,
    memory_usage_mb DOUBLE PRECISION,
    custom_metrics JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT performance_metrics_agent_fk FOREIGN KEY (agent_id) REFERENCES ai_agents(agent_id) ON DELETE CASCADE,
    CONSTRAINT performance_metrics_timestamp_not_future CHECK (timestamp <= CURRENT_TIMESTAMP),
    CONSTRAINT performance_metrics_latency_positive CHECK (latency_ms IS NULL OR latency_ms > 0),
    CONSTRAINT performance_metrics_memory_positive CHECK (memory_usage_mb IS NULL OR memory_usage_mb > 0),
    CONSTRAINT performance_metrics_cpu_percent_valid CHECK (cpu_usage_percent IS NULL OR (cpu_usage_percent >= 0 AND cpu_usage_percent <= 100)),
    CONSTRAINT performance_metrics_gpu_percent_valid CHECK (gpu_usage_percent IS NULL OR (gpu_usage_percent >= 0 AND gpu_usage_percent <= 100)),
    CONSTRAINT performance_metrics_at_least_one_metric CHECK (
        latency_ms IS NOT NULL OR 
        throughput_req_per_min IS NOT NULL OR 
        cost_per_request IS NOT NULL OR 
        cpu_usage_percent IS NOT NULL OR 
        gpu_usage_percent IS NOT NULL OR 
        memory_usage_mb IS NOT NULL OR 
        jsonb_array_length(custom_metrics::jsonb) > 0
    )
) PARTITION BY RANGE (timestamp);

-- User Sessions table
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_identifier VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    active_filters JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT user_sessions_user_not_empty CHECK (length(trim(user_identifier)) > 0),
    CONSTRAINT user_sessions_activity_order CHECK (last_activity >= created_at)
);

-- Monitoring Configuration table
CREATE TABLE monitoring_configuration (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID,
    collection_interval_seconds INTEGER NOT NULL DEFAULT 60,
    retention_days INTEGER NOT NULL DEFAULT 90,
    alert_thresholds JSONB DEFAULT '{}',
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT monitoring_config_agent_fk FOREIGN KEY (agent_id) REFERENCES ai_agents(agent_id) ON DELETE CASCADE,
    CONSTRAINT monitoring_config_interval_valid CHECK (collection_interval_seconds BETWEEN 1 AND 3600),
    CONSTRAINT monitoring_config_retention_positive CHECK (retention_days > 0)
);

-- Create indexes for optimal performance
CREATE INDEX idx_ai_agents_name ON ai_agents (name);
CREATE INDEX idx_ai_agents_status ON ai_agents (status) WHERE status != 'running';
CREATE INDEX idx_ai_agents_last_seen ON ai_agents (last_seen DESC);

CREATE INDEX idx_metrics_agent_timestamp ON performance_metrics (agent_id, timestamp DESC);
CREATE INDEX idx_metrics_timestamp ON performance_metrics (timestamp DESC);

CREATE INDEX idx_sessions_user_activity ON user_sessions (user_identifier, last_activity DESC);
CREATE INDEX idx_sessions_last_activity ON user_sessions (last_activity DESC);

CREATE INDEX idx_config_agent_enabled ON monitoring_configuration (agent_id, enabled);

-- Create unique constraints
CREATE UNIQUE INDEX idx_ai_agents_name_unique ON ai_agents (name);

-- Create initial partitions for performance_metrics (current month and next month)
CREATE TABLE performance_metrics_default PARTITION OF performance_metrics DEFAULT;

-- Function to create monthly partitions automatically
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Create partitions for current month and next few months
SELECT create_monthly_partition('performance_metrics', date_trunc('month', CURRENT_DATE));
SELECT create_monthly_partition('performance_metrics', date_trunc('month', CURRENT_DATE + INTERVAL '1 month'));
SELECT create_monthly_partition('performance_metrics', date_trunc('month', CURRENT_DATE + INTERVAL '2 months'));

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to monitoring_configuration
CREATE TRIGGER update_monitoring_configuration_updated_at
    BEFORE UPDATE ON monitoring_configuration
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default global configuration
INSERT INTO monitoring_configuration (agent_id, collection_interval_seconds, retention_days, alert_thresholds)
VALUES (
    NULL,
    60,
    90,
    '{
        "latency_ms": {"warning": 1000, "critical": 5000},
        "cpu_usage_percent": {"warning": 80, "critical": 95},
        "memory_usage_mb": {"warning": 1000, "critical": 2000},
        "error_rate_percent": {"warning": 5, "critical": 10}
    }'::jsonb
);

-- Create views for common queries
CREATE VIEW agent_summary AS
SELECT 
    a.agent_id,
    a.name,
    a.status,
    a.created_at,
    a.last_seen,
    COUNT(m.metric_id) as total_metrics,
    MAX(m.timestamp) as latest_metric_timestamp
FROM ai_agents a
LEFT JOIN performance_metrics m ON a.agent_id = m.agent_id
GROUP BY a.agent_id, a.name, a.status, a.created_at, a.last_seen;

CREATE VIEW recent_metrics AS
SELECT 
    m.*,
    a.name as agent_name,
    a.status as agent_status
FROM performance_metrics m
JOIN ai_agents a ON m.agent_id = a.agent_id
WHERE m.timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
ORDER BY m.timestamp DESC;

-- Grant appropriate permissions
-- These would be customized based on application user roles
GRANT SELECT, INSERT, UPDATE ON ai_agents TO sentinel_app;
GRANT SELECT, INSERT ON performance_metrics TO sentinel_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO sentinel_app;
GRANT SELECT, INSERT, UPDATE ON monitoring_configuration TO sentinel_app;
GRANT SELECT ON agent_summary TO sentinel_app;
GRANT SELECT ON recent_metrics TO sentinel_app;