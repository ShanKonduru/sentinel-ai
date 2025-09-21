-- Sample data for development and testing
-- Version: 1.0.0
-- This file inserts sample data for local development

-- Sample AI Agents
INSERT INTO ai_agents (agent_id, name, description, status, last_seen) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'GPT-4 Assistant', 'Main conversational AI agent', 'running', CURRENT_TIMESTAMP - INTERVAL '2 minutes'),
('550e8400-e29b-41d4-a716-446655440002', 'Code Review Bot', 'Automated code review and analysis', 'running', CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
('550e8400-e29b-41d4-a716-446655440003', 'Data Processor', 'Batch data processing agent', 'stopped', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
('550e8400-e29b-41d4-a716-446655440004', 'Translation Service', 'Multi-language translation agent', 'error', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
('550e8400-e29b-41d4-a716-446655440005', 'Image Generator', 'AI image generation service', 'unknown', CURRENT_TIMESTAMP - INTERVAL '30 minutes');

-- Sample Performance Metrics (last 24 hours)
INSERT INTO performance_metrics (agent_id, timestamp, latency_ms, throughput_req_per_min, cost_per_request, cpu_usage_percent, memory_usage_mb) VALUES
-- GPT-4 Assistant metrics
('550e8400-e29b-41d4-a716-446655440001', CURRENT_TIMESTAMP - INTERVAL '1 minute', 250.5, 120.0, 0.05, 45.2, 512.0),
('550e8400-e29b-41d4-a716-446655440001', CURRENT_TIMESTAMP - INTERVAL '2 minutes', 180.3, 135.0, 0.04, 42.1, 498.5),
('550e8400-e29b-41d4-a716-446655440001', CURRENT_TIMESTAMP - INTERVAL '5 minutes', 320.1, 98.5, 0.06, 48.7, 525.3),
('550e8400-e29b-41d4-a716-446655440001', CURRENT_TIMESTAMP - INTERVAL '10 minutes', 195.8, 142.3, 0.03, 39.4, 487.2),
('550e8400-e29b-41d4-a716-446655440001', CURRENT_TIMESTAMP - INTERVAL '15 minutes', 275.2, 118.7, 0.05, 46.8, 515.8),

-- Code Review Bot metrics
('550e8400-e29b-41d4-a716-446655440002', CURRENT_TIMESTAMP - INTERVAL '3 minutes', 450.2, 45.2, 0.08, 65.3, 768.9),
('550e8400-e29b-41d4-a716-446655440002', CURRENT_TIMESTAMP - INTERVAL '8 minutes', 380.7, 52.1, 0.07, 62.1, 745.2),
('550e8400-e29b-41d4-a716-446655440002', CURRENT_TIMESTAMP - INTERVAL '13 minutes', 520.3, 38.5, 0.09, 68.9, 785.4),
('550e8400-e29b-41d4-a716-446655440002', CURRENT_TIMESTAMP - INTERVAL '18 minutes', 395.1, 48.7, 0.08, 63.7, 752.8),

-- Translation Service metrics (before error)
('550e8400-e29b-41d4-a716-446655440004', CURRENT_TIMESTAMP - INTERVAL '12 minutes', 125.4, 85.3, 0.02, 35.2, 298.7),
('550e8400-e29b-41d4-a716-446655440004', CURRENT_TIMESTAMP - INTERVAL '15 minutes', 98.7, 92.1, 0.02, 32.8, 285.3),
('550e8400-e29b-41d4-a716-446655440004', CURRENT_TIMESTAMP - INTERVAL '20 minutes', 142.3, 78.9, 0.03, 38.1, 312.5),

-- Image Generator metrics
('550e8400-e29b-41d4-a716-446655440005', CURRENT_TIMESTAMP - INTERVAL '32 minutes', 2500.8, 12.3, 0.25, 85.7, 1250.4),
('550e8400-e29b-41d4-a716-446655440005', CURRENT_TIMESTAMP - INTERVAL '35 minutes', 2150.2, 15.1, 0.22, 82.3, 1185.7),
('550e8400-e29b-41d4-a716-446655440005', CURRENT_TIMESTAMP - INTERVAL '40 minutes', 2750.5, 10.8, 0.28, 88.9, 1325.2);

-- Sample User Sessions
INSERT INTO user_sessions (session_id, user_identifier, preferences, active_filters) VALUES
('650e8400-e29b-41d4-a716-446655440001', 'admin@example.com', '{"theme": "dark", "refresh_interval": 30}', '{"agent_ids": ["550e8400-e29b-41d4-a716-446655440001"], "time_range": "1h"}'),
('650e8400-e29b-41d4-a716-446655440002', 'developer@example.com', '{"theme": "light", "refresh_interval": 60}', '{"status": ["running", "error"], "time_range": "24h"}'),
('650e8400-e29b-41d4-a716-446655440003', 'analyst@example.com', '{"theme": "light", "dashboard_view": "compact"}', '{"time_range": "7d"}');

-- Sample Monitoring Configuration (agent-specific)
INSERT INTO monitoring_configuration (agent_id, collection_interval_seconds, retention_days, alert_thresholds) VALUES
('550e8400-e29b-41d4-a716-446655440001', 30, 180, '{"latency_ms": {"warning": 500, "critical": 1000}}'),
('550e8400-e29b-41d4-a716-446655440002', 60, 365, '{"latency_ms": {"warning": 800, "critical": 2000}, "cpu_usage_percent": {"warning": 70, "critical": 90}}'),
('550e8400-e29b-41d4-a716-446655440005', 120, 90, '{"latency_ms": {"warning": 3000, "critical": 5000}, "memory_usage_mb": {"warning": 1500, "critical": 2000}}');