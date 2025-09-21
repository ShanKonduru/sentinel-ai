/**
 * Integration test for Dashboard Filtering functionality.
 * 
 * This test simulates the complete workflow of dashboard users applying
 * various filters to focus on specific agents, time ranges, and metrics.
 * 
 * Based on user scenarios from spec - MUST FAIL before implementation.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '../src/components/Dashboard';
import { MetricsProvider } from '../src/services/MetricsService';

describe('Dashboard Filtering Integration', () => {
  let mockFetch: any;
  let user: any;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Mock fetch for API calls
    mockFetch = vi.fn();
    global.fetch = mockFetch;
    
    // Setup user event for interactions
    user = userEvent.setup();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should filter agents by performance metrics thresholds', async () => {
    // This WILL FAIL until dashboard filtering is implemented

    // Step 1: Setup diverse agent data for filtering
    const diverseMetricsResponse = {
      metrics: [
        {
          agent_id: 'fast-agent-1',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 80,
          cpu_usage_percent: 30,
          memory_usage_mb: 1500,
          error_rate_percent: 0.5,
          status: 'healthy'
        },
        {
          agent_id: 'slow-agent-1', 
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 2500,
          cpu_usage_percent: 85,
          memory_usage_mb: 6000,
          error_rate_percent: 12,
          status: 'degraded'
        },
        {
          agent_id: 'medium-agent-1',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 200,
          cpu_usage_percent: 55,
          memory_usage_mb: 3000,
          error_rate_percent: 2,
          status: 'healthy'
        },
        {
          agent_id: 'critical-agent-1',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 5000,
          cpu_usage_percent: 95,
          memory_usage_mb: 8000,
          error_rate_percent: 25,
          status: 'critical'
        }
      ]
    };

    const agentsResponse = {
      agents: diverseMetricsResponse.metrics.map(m => ({
        agent_id: m.agent_id,
        status: m.status,
        last_seen: m.timestamp
      }))
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(diverseMetricsResponse)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(agentsResponse)
      });

    // Step 2: Render dashboard with filtering enabled
    render(
      <MetricsProvider>
        <Dashboard showFilters={true} />
      </MetricsProvider>
    );

    // Verify all agents are initially displayed
    await waitFor(() => {
      expect(screen.getByText('fast-agent-1')).toBeInTheDocument();
      expect(screen.getByText('slow-agent-1')).toBeInTheDocument();
      expect(screen.getByText('medium-agent-1')).toBeInTheDocument();
      expect(screen.getByText('critical-agent-1')).toBeInTheDocument();
    });

    // Step 3: Apply latency filter (< 500ms)
    const latencyFilter = screen.getByLabelText('Max Latency (ms)');
    await user.clear(latencyFilter);
    await user.type(latencyFilter, '500');
    await user.tab(); // Trigger filter application

    // Should show only agents with latency < 500ms
    await waitFor(() => {
      expect(screen.getByText('fast-agent-1')).toBeInTheDocument();    // 80ms
      expect(screen.getByText('medium-agent-1')).toBeInTheDocument();  // 200ms
      expect(screen.queryByText('slow-agent-1')).not.toBeInTheDocument();    // 2500ms - filtered out
      expect(screen.queryByText('critical-agent-1')).not.toBeInTheDocument(); // 5000ms - filtered out
    });

    // Step 4: Apply additional CPU filter (< 60%)
    const cpuFilter = screen.getByLabelText('Max CPU Usage (%)');
    await user.clear(cpuFilter);
    await user.type(cpuFilter, '60');
    await user.tab();

    // Should show only agents meeting both criteria
    await waitFor(() => {
      expect(screen.getByText('fast-agent-1')).toBeInTheDocument();     // 80ms latency, 30% CPU
      expect(screen.getByText('medium-agent-1')).toBeInTheDocument();   // 200ms latency, 55% CPU
      // slow-agent-1 and critical-agent-1 already filtered by latency
    });

    // Step 5: Apply stricter CPU filter (< 40%)
    await user.clear(cpuFilter);
    await user.type(cpuFilter, '40');
    await user.tab();

    // Should show only fast-agent-1 now
    await waitFor(() => {
      expect(screen.getByText('fast-agent-1')).toBeInTheDocument();     // 30% CPU
      expect(screen.queryByText('medium-agent-1')).not.toBeInTheDocument(); // 55% CPU - filtered out
    });

    // Step 6: Clear filters and verify all agents return
    const clearFiltersButton = screen.getByText('Clear Filters');
    await user.click(clearFiltersButton);

    await waitFor(() => {
      expect(screen.getByText('fast-agent-1')).toBeInTheDocument();
      expect(screen.getByText('slow-agent-1')).toBeInTheDocument();
      expect(screen.getByText('medium-agent-1')).toBeInTheDocument();
      expect(screen.getByText('critical-agent-1')).toBeInTheDocument();
    });
  });

  it('should filter agents by status and environment tags', async () => {
    // This WILL FAIL until tag-based filtering is implemented

    // Setup agents with different statuses and environments
    const taggedAgentsResponse = {
      metrics: [
        {
          agent_id: 'prod-healthy-1',
          environment: 'production',
          status: 'healthy',
          team: 'backend',
          latency_ms: 150
        },
        {
          agent_id: 'prod-degraded-1',
          environment: 'production', 
          status: 'degraded',
          team: 'frontend',
          latency_ms: 800
        },
        {
          agent_id: 'staging-healthy-1',
          environment: 'staging',
          status: 'healthy',
          team: 'backend', 
          latency_ms: 120
        },
        {
          agent_id: 'dev-critical-1',
          environment: 'development',
          status: 'critical',
          team: 'ml',
          latency_ms: 3000
        }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(taggedAgentsResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showTagFilters={true} />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('prod-healthy-1')).toBeInTheDocument();
      expect(screen.getByText('prod-degraded-1')).toBeInTheDocument();
      expect(screen.getByText('staging-healthy-1')).toBeInTheDocument();
      expect(screen.getByText('dev-critical-1')).toBeInTheDocument();
    });

    // Step 1: Filter by environment (production only)
    const environmentFilter = screen.getByLabelText('Environment');
    await user.selectOptions(environmentFilter, 'production');

    await waitFor(() => {
      expect(screen.getByText('prod-healthy-1')).toBeInTheDocument();
      expect(screen.getByText('prod-degraded-1')).toBeInTheDocument();
      expect(screen.queryByText('staging-healthy-1')).not.toBeInTheDocument();
      expect(screen.queryByText('dev-critical-1')).not.toBeInTheDocument();
    });

    // Step 2: Add status filter (healthy only)
    const statusFilter = screen.getByLabelText('Status');
    await user.selectOptions(statusFilter, 'healthy');

    await waitFor(() => {
      expect(screen.getByText('prod-healthy-1')).toBeInTheDocument();
      expect(screen.queryByText('prod-degraded-1')).not.toBeInTheDocument(); // Not healthy
    });

    // Step 3: Change environment to staging (should show staging-healthy-1)
    await user.selectOptions(environmentFilter, 'staging');

    await waitFor(() => {
      expect(screen.queryByText('prod-healthy-1')).not.toBeInTheDocument();
      expect(screen.getByText('staging-healthy-1')).toBeInTheDocument(); // staging + healthy
    });

    // Step 4: Filter by team (backend)
    const teamFilter = screen.getByLabelText('Team');
    await user.selectOptions(teamFilter, 'backend');

    await waitFor(() => {
      expect(screen.getByText('staging-healthy-1')).toBeInTheDocument(); // staging + healthy + backend
    });

    // If we change to production environment with same filters
    await user.selectOptions(environmentFilter, 'production');

    await waitFor(() => {
      expect(screen.getByText('prod-healthy-1')).toBeInTheDocument(); // production + healthy + backend
      expect(screen.queryByText('staging-healthy-1')).not.toBeInTheDocument();
    });
  });

  it('should filter agents by time range and show historical data', async () => {
    // This WILL FAIL until time-based filtering is implemented

    // Setup historical metrics data
    const historicalResponse = {
      metrics: [
        // Recent data (last hour)
        {
          agent_id: 'time-agent-1',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 150,
          period: 'recent'
        },
        {
          agent_id: 'time-agent-2', 
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 200,
          period: 'recent'
        },
        // Older data (6 hours ago)
        {
          agent_id: 'time-agent-1',
          timestamp: '2025-09-21T00:00:00Z',
          latency_ms: 300,
          period: 'older'
        },
        {
          agent_id: 'time-agent-3',
          timestamp: '2025-09-21T00:00:00Z',
          latency_ms: 180,
          period: 'older'
        },
        // Very old data (24 hours ago)
        {
          agent_id: 'time-agent-1',
          timestamp: '2025-09-20T06:00:00Z',
          latency_ms: 400,
          period: 'oldest'
        }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(historicalResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showTimeFilter={true} />
      </MetricsProvider>
    );

    // By default, should show recent data
    await waitFor(() => {
      expect(screen.getByText('time-agent-1')).toBeInTheDocument();
      expect(screen.getByText('time-agent-2')).toBeInTheDocument();
      expect(screen.getByText('150ms')).toBeInTheDocument(); // Recent latency for agent-1
    });

    // Step 1: Change time range to last 6 hours
    const timeRangeFilter = screen.getByLabelText('Time Range');
    await user.selectOptions(timeRangeFilter, '6h');

    // Should trigger new API call with time range
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('start_date='),
        expect.any(Object)
      );
    });

    // Mock response for 6-hour range
    const sixHourResponse = {
      metrics: historicalResponse.metrics.filter(m => 
        m.period === 'recent' || m.period === 'older'
      )
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(sixHourResponse)
    });

    await waitFor(() => {
      expect(screen.getByText('time-agent-1')).toBeInTheDocument();
      expect(screen.getByText('time-agent-2')).toBeInTheDocument();
      expect(screen.getByText('time-agent-3')).toBeInTheDocument(); // Now visible
    });

    // Step 2: Change to 24-hour range
    await user.selectOptions(timeRangeFilter, '24h');

    const twentyFourHourResponse = {
      metrics: historicalResponse.metrics // All data
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(twentyFourHourResponse)
    });

    await waitFor(() => {
      // Should show aggregated or latest data for each agent
      expect(screen.getByText('time-agent-1')).toBeInTheDocument();
      expect(screen.getByText('time-agent-2')).toBeInTheDocument();
      expect(screen.getByText('time-agent-3')).toBeInTheDocument();
    });

    // Step 3: Apply custom date range
    const customDateButton = screen.getByText('Custom Range');
    await user.click(customDateButton);

    const startDateInput = screen.getByLabelText('Start Date');
    const endDateInput = screen.getByLabelText('End Date');

    await user.type(startDateInput, '2025-09-20');
    await user.type(endDateInput, '2025-09-21');

    const applyDateRangeButton = screen.getByText('Apply Date Range');
    await user.click(applyDateRangeButton);

    // Should trigger API call with custom date range
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('start_date=2025-09-20'),
        expect.any(Object)
      );
    });
  });

  it('should combine multiple filters and show filter summary', async () => {
    // This WILL FAIL until combined filtering is implemented

    const complexFilteringResponse = {
      metrics: [
        {
          agent_id: 'filter-agent-1',
          environment: 'production',
          status: 'healthy',
          latency_ms: 100,
          cpu_usage_percent: 40,
          team: 'backend'
        },
        {
          agent_id: 'filter-agent-2',
          environment: 'production',
          status: 'degraded',
          latency_ms: 600,
          cpu_usage_percent: 70,
          team: 'frontend'
        },
        {
          agent_id: 'filter-agent-3',
          environment: 'staging',
          status: 'healthy',
          latency_ms: 150,
          cpu_usage_percent: 45,
          team: 'backend'
        }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(complexFilteringResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showAdvancedFilters={true} />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('filter-agent-1')).toBeInTheDocument();
      expect(screen.getByText('filter-agent-2')).toBeInTheDocument();
      expect(screen.getByText('filter-agent-3')).toBeInTheDocument();
    });

    // Step 1: Apply environment filter
    const environmentFilter = screen.getByLabelText('Environment');
    await user.selectOptions(environmentFilter, 'production');

    await waitFor(() => {
      expect(screen.getByText('filter-agent-1')).toBeInTheDocument();
      expect(screen.getByText('filter-agent-2')).toBeInTheDocument();
      expect(screen.queryByText('filter-agent-3')).not.toBeInTheDocument();
    });

    // Verify filter summary shows active filter
    expect(screen.getByText('Environment: production')).toBeInTheDocument();
    expect(screen.getByText('Showing 2 of 3 agents')).toBeInTheDocument();

    // Step 2: Add latency filter
    const latencyFilter = screen.getByLabelText('Max Latency (ms)');
    await user.type(latencyFilter, '500');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('filter-agent-1')).toBeInTheDocument(); // 100ms latency
      expect(screen.queryByText('filter-agent-2')).not.toBeInTheDocument(); // 600ms - filtered out
    });

    // Verify updated filter summary
    expect(screen.getByText('Environment: production')).toBeInTheDocument();
    expect(screen.getByText('Max Latency: 500ms')).toBeInTheDocument();
    expect(screen.getByText('Showing 1 of 3 agents')).toBeInTheDocument();

    // Step 3: Add team filter
    const teamFilter = screen.getByLabelText('Team');
    await user.selectOptions(teamFilter, 'backend');

    await waitFor(() => {
      expect(screen.getByText('filter-agent-1')).toBeInTheDocument(); // production + <500ms + backend
    });

    // Verify comprehensive filter summary
    expect(screen.getByText('Environment: production')).toBeInTheDocument();
    expect(screen.getByText('Max Latency: 500ms')).toBeInTheDocument();
    expect(screen.getByText('Team: backend')).toBeInTheDocument();
    expect(screen.getByText('Showing 1 of 3 agents')).toBeInTheDocument();

    // Step 4: Remove one filter (environment)
    const removeEnvironmentFilter = within(
      screen.getByText('Environment: production').parentElement!
    ).getByRole('button', { name: /remove/i });
    await user.click(removeEnvironmentFilter);

    await waitFor(() => {
      expect(screen.getByText('filter-agent-1')).toBeInTheDocument(); // production backend <500ms
      expect(screen.getByText('filter-agent-3')).toBeInTheDocument(); // staging backend <500ms
    });

    // Verify updated summary
    expect(screen.queryByText('Environment: production')).not.toBeInTheDocument();
    expect(screen.getByText('Max Latency: 500ms')).toBeInTheDocument();
    expect(screen.getByText('Team: backend')).toBeInTheDocument();
    expect(screen.getByText('Showing 2 of 3 agents')).toBeInTheDocument();
  });

  it('should save and restore filter presets', async () => {
    // This WILL FAIL until filter presets are implemented

    const presetResponse = {
      metrics: [
        { agent_id: 'preset-agent-1', environment: 'production', status: 'healthy', latency_ms: 100 },
        { agent_id: 'preset-agent-2', environment: 'production', status: 'degraded', latency_ms: 800 },
        { agent_id: 'preset-agent-3', environment: 'staging', status: 'healthy', latency_ms: 120 }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(presetResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showFilterPresets={true} />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('preset-agent-1')).toBeInTheDocument();
    });

    // Step 1: Apply multiple filters
    const environmentFilter = screen.getByLabelText('Environment');
    await user.selectOptions(environmentFilter, 'production');

    const statusFilter = screen.getByLabelText('Status');
    await user.selectOptions(statusFilter, 'healthy');

    await waitFor(() => {
      expect(screen.getByText('preset-agent-1')).toBeInTheDocument();
      expect(screen.queryByText('preset-agent-2')).not.toBeInTheDocument();
      expect(screen.queryByText('preset-agent-3')).not.toBeInTheDocument();
    });

    // Step 2: Save filter preset
    const savePresetButton = screen.getByText('Save Filter Preset');
    await user.click(savePresetButton);

    const presetNameInput = screen.getByLabelText('Preset Name');
    await user.type(presetNameInput, 'Healthy Production Agents');

    const confirmSaveButton = screen.getByText('Save Preset');
    await user.click(confirmSaveButton);

    // Verify preset appears in list
    await waitFor(() => {
      expect(screen.getByText('Healthy Production Agents')).toBeInTheDocument();
    });

    // Step 3: Clear filters
    const clearFiltersButton = screen.getByText('Clear Filters');
    await user.click(clearFiltersButton);

    await waitFor(() => {
      expect(screen.getByText('preset-agent-1')).toBeInTheDocument();
      expect(screen.getByText('preset-agent-2')).toBeInTheDocument();
      expect(screen.getByText('preset-agent-3')).toBeInTheDocument();
    });

    // Step 4: Apply saved preset
    const presetButton = screen.getByText('Healthy Production Agents');
    await user.click(presetButton);

    // Should restore the same filter state
    await waitFor(() => {
      expect(screen.getByText('preset-agent-1')).toBeInTheDocument();
      expect(screen.queryByText('preset-agent-2')).not.toBeInTheDocument();
      expect(screen.queryByText('preset-agent-3')).not.toBeInTheDocument();
    });

    // Verify filters are restored
    expect(environmentFilter).toHaveValue('production');
    expect(statusFilter).toHaveValue('healthy');
  });

  it('should provide search functionality with filter integration', async () => {
    // This WILL FAIL until search with filtering is implemented

    const searchableResponse = {
      metrics: [
        { agent_id: 'web-server-prod-1', type: 'web', environment: 'production', latency_ms: 150 },
        { agent_id: 'web-server-dev-1', type: 'web', environment: 'development', latency_ms: 120 },
        { agent_id: 'api-gateway-prod-1', type: 'api', environment: 'production', latency_ms: 200 },
        { agent_id: 'ml-worker-prod-1', type: 'ml', environment: 'production', latency_ms: 800 },
        { agent_id: 'database-replica-1', type: 'database', environment: 'production', latency_ms: 50 }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(searchableResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showSearch={true} showFilters={true} />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument();
      expect(screen.getByText('api-gateway-prod-1')).toBeInTheDocument();
    });

    // Step 1: Search for "web" agents
    const searchInput = screen.getByPlaceholderText('Search agents...');
    await user.type(searchInput, 'web');

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument();
      expect(screen.getByText('web-server-dev-1')).toBeInTheDocument();
      expect(screen.queryByText('api-gateway-prod-1')).not.toBeInTheDocument();
      expect(screen.queryByText('ml-worker-prod-1')).not.toBeInTheDocument();
    });

    // Step 2: Apply environment filter while search is active
    const environmentFilter = screen.getByLabelText('Environment');
    await user.selectOptions(environmentFilter, 'production');

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument(); // web + production
      expect(screen.queryByText('web-server-dev-1')).not.toBeInTheDocument(); // web but not production
    });

    // Step 3: Change search to "server"
    await user.clear(searchInput);
    await user.type(searchInput, 'server');

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument(); // server + production
      expect(screen.queryByText('api-gateway-prod-1')).not.toBeInTheDocument(); // production but not server
    });

    // Step 4: Clear search, keep filter
    await user.clear(searchInput);

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument();
      expect(screen.getByText('api-gateway-prod-1')).toBeInTheDocument();
      expect(screen.getByText('ml-worker-prod-1')).toBeInTheDocument();
      expect(screen.getByText('database-replica-1')).toBeInTheDocument();
      expect(screen.queryByText('web-server-dev-1')).not.toBeInTheDocument(); // Still filtered by environment
    });

    // Step 5: Advanced search with operators
    await user.type(searchInput, 'type:web OR type:api');

    await waitFor(() => {
      expect(screen.getByText('web-server-prod-1')).toBeInTheDocument(); // web + production
      expect(screen.getByText('api-gateway-prod-1')).toBeInTheDocument(); // api + production
      expect(screen.queryByText('ml-worker-prod-1')).not.toBeInTheDocument(); // ml type
      expect(screen.queryByText('database-replica-1')).not.toBeInTheDocument(); // database type
    });
  });
});