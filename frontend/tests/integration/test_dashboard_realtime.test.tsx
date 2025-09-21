/**
 * Integration test for Dashboard Real-time Updates functionality.
 * 
 * This test simulates the complete workflow of dashboard users viewing
 * real-time performance metrics as they stream in from agents.
 * 
 * Based on user scenarios from spec - MUST FAIL before implementation.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { WebSocket } from 'ws';
import Dashboard from '../src/components/Dashboard';
import { MetricsProvider } from '../src/services/MetricsService';

// Mock WebSocket for real-time testing
global.WebSocket = vi.fn(() => ({
  onopen: vi.fn(),
  onmessage: vi.fn(),
  onclose: vi.fn(),
  onerror: vi.fn(),
  send: vi.fn(),
  close: vi.fn(),
  readyState: WebSocket.OPEN
}));

describe('Dashboard Real-time Updates Integration', () => {
  let mockWebSocket: any;
  let mockFetch: any;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Mock fetch for initial data loading
    mockFetch = vi.fn();
    global.fetch = mockFetch;
    
    // Mock WebSocket instance
    mockWebSocket = {
      onopen: vi.fn(),
      onmessage: vi.fn(),
      onclose: vi.fn(),
      onerror: vi.fn(),
      send: vi.fn(),
      close: vi.fn(),
      readyState: 1, // OPEN
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    };
    
    // Make WebSocket constructor return our mock
    (global.WebSocket as any).mockImplementation(() => mockWebSocket);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should establish real-time connection and display live metrics', async () => {
    // This WILL FAIL until dashboard real-time functionality is implemented

    // Step 1: Mock initial API response for dashboard load
    const initialMetricsResponse = {
      metrics: [
        {
          agent_id: 'agent-1',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 150,
          cpu_usage_percent: 45,
          memory_usage_mb: 2000,
          throughput_req_per_min: 60
        },
        {
          agent_id: 'agent-2', 
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 200,
          cpu_usage_percent: 55,
          memory_usage_mb: 2500,
          throughput_req_per_min: 50
        }
      ]
    };

    const agentsResponse = {
      agents: [
        {
          agent_id: 'agent-1',
          status: 'healthy',
          last_seen: '2025-09-21T06:00:00Z'
        },
        {
          agent_id: 'agent-2',
          status: 'healthy',
          last_seen: '2025-09-21T06:00:00Z'
        }
      ]
    };

    // Mock initial data fetches
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(initialMetricsResponse)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(agentsResponse)
      });

    // Step 2: Render dashboard component
    render(
      <MetricsProvider>
        <Dashboard />
      </MetricsProvider>
    );

    // Step 3: Verify initial data loads
    await waitFor(() => {
      expect(screen.getByText('agent-1')).toBeInTheDocument();
      expect(screen.getByText('agent-2')).toBeInTheDocument();
    });

    // Verify initial metrics are displayed
    expect(screen.getByText('150ms')).toBeInTheDocument(); // agent-1 latency
    expect(screen.getByText('200ms')).toBeInTheDocument(); // agent-2 latency
    expect(screen.getByText('45%')).toBeInTheDocument();   // agent-1 CPU
    expect(screen.getByText('55%')).toBeInTheDocument();   // agent-2 CPU

    // Step 4: Verify WebSocket connection is established
    expect(global.WebSocket).toHaveBeenCalledWith(
      expect.stringContaining('ws://localhost:5000/ws/metrics')
    );
    expect(mockWebSocket.onopen).toBeDefined();
    expect(mockWebSocket.onmessage).toBeDefined();

    // Step 5: Simulate real-time metric updates
    const realTimeUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'agent-1',
        timestamp: '2025-09-21T06:01:00Z',
        latency_ms: 250,  // Increased latency
        cpu_usage_percent: 75,  // Increased CPU
        memory_usage_mb: 2200,
        throughput_req_per_min: 55
      }
    };

    // Trigger WebSocket message
    const messageEvent = new MessageEvent('message', {
      data: JSON.stringify(realTimeUpdate)
    });
    mockWebSocket.onmessage(messageEvent);

    // Step 6: Verify UI updates with new real-time data
    await waitFor(() => {
      expect(screen.getByText('250ms')).toBeInTheDocument(); // Updated latency
      expect(screen.getByText('75%')).toBeInTheDocument();   // Updated CPU
    });

    // Verify old values are no longer displayed for agent-1
    expect(screen.queryByText('150ms')).not.toBeInTheDocument();
    expect(screen.queryByText('45%')).not.toBeInTheDocument();

    // agent-2 should still have original values (not updated)
    expect(screen.getByText('200ms')).toBeInTheDocument();
    expect(screen.getByText('55%')).toBeInTheDocument();
  });

  it('should handle multiple rapid real-time updates efficiently', async () => {
    // This WILL FAIL until efficient real-time handling is implemented

    // Setup initial dashboard state
    const initialResponse = {
      metrics: [{
        agent_id: 'performance-agent',
        timestamp: '2025-09-21T06:00:00Z',
        latency_ms: 100,
        cpu_usage_percent: 30,
        memory_usage_mb: 1500
      }]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(initialResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('performance-agent')).toBeInTheDocument();
    });

    // Step 1: Simulate rapid burst of updates (10 updates in quick succession)
    const updates = [];
    for (let i = 1; i <= 10; i++) {
      updates.push({
        type: 'metric_update',
        data: {
          agent_id: 'performance-agent',
          timestamp: `2025-09-21T06:0${i}:00Z`,
          latency_ms: 100 + (i * 50),  // Gradually increasing
          cpu_usage_percent: 30 + (i * 5),
          memory_usage_mb: 1500 + (i * 100),
          sequence_number: i
        }
      });
    }

    // Step 2: Send all updates rapidly
    updates.forEach((update, index) => {
      setTimeout(() => {
        const messageEvent = new MessageEvent('message', {
          data: JSON.stringify(update)
        });
        mockWebSocket.onmessage(messageEvent);
      }, index * 10); // 10ms apart
    });

    // Step 3: Verify final state reflects latest update (not intermediate ones)
    await waitFor(() => {
      expect(screen.getByText('600ms')).toBeInTheDocument(); // Final latency (100 + 10*50)
      expect(screen.getByText('80%')).toBeInTheDocument();   // Final CPU (30 + 10*5)
    }, { timeout: 5000 });

    // Should not show intermediate values
    expect(screen.queryByText('300ms')).not.toBeInTheDocument(); // Intermediate value
    expect(screen.queryByText('50%')).not.toBeInTheDocument();   // Intermediate value
  });

  it('should display real-time alerts for performance issues', async () => {
    // This WILL FAIL until real-time alerting is implemented

    // Setup initial healthy state
    const initialResponse = {
      metrics: [{
        agent_id: 'alert-test-agent',
        timestamp: '2025-09-21T06:00:00Z',
        latency_ms: 120,
        cpu_usage_percent: 40,
        memory_usage_mb: 1800,
        error_rate_percent: 0.5
      }]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(initialResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('alert-test-agent')).toBeInTheDocument();
    });

    // Verify no alerts initially
    expect(screen.queryByText(/alert/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/warning/i)).not.toBeInTheDocument();

    // Step 1: Send update that triggers performance alert
    const alertTrigger = {
      type: 'metric_update',
      data: {
        agent_id: 'alert-test-agent',
        timestamp: '2025-09-21T06:01:00Z',
        latency_ms: 3000,    // High latency - should trigger alert
        cpu_usage_percent: 95, // High CPU - should trigger alert
        memory_usage_mb: 7500, // High memory - should trigger alert
        error_rate_percent: 15 // High error rate - should trigger alert
      }
    };

    const messageEvent = new MessageEvent('message', {
      data: JSON.stringify(alertTrigger)
    });
    mockWebSocket.onmessage(messageEvent);

    // Step 2: Verify real-time alerts appear
    await waitFor(() => {
      expect(screen.getByText(/high latency/i)).toBeInTheDocument();
      expect(screen.getByText(/high cpu usage/i)).toBeInTheDocument();
      expect(screen.getByText(/high memory usage/i)).toBeInTheDocument();
      expect(screen.getByText(/high error rate/i)).toBeInTheDocument();
    });

    // Step 3: Verify alert severity indicators
    const alertElements = screen.getAllByRole('alert');
    expect(alertElements.length).toBeGreaterThan(0);

    // Should have critical severity for multiple high values
    expect(screen.getByText(/critical/i)).toBeInTheDocument();

    // Step 4: Send recovery update
    const recoveryUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'alert-test-agent',
        timestamp: '2025-09-21T06:02:00Z',
        latency_ms: 130,     // Back to normal
        cpu_usage_percent: 42, // Back to normal
        memory_usage_mb: 1900, // Back to normal
        error_rate_percent: 0.8 // Back to normal
      }
    };

    const recoveryEvent = new MessageEvent('message', {
      data: JSON.stringify(recoveryUpdate)
    });
    mockWebSocket.onmessage(recoveryEvent);

    // Step 5: Verify alerts clear when metrics return to normal
    await waitFor(() => {
      expect(screen.queryByText(/high latency/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/high cpu usage/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/critical/i)).not.toBeInTheDocument();
    });
  });

  it('should maintain real-time connection resilience', async () => {
    // This WILL FAIL until connection resilience is implemented

    // Setup initial dashboard
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ metrics: [], agents: [] })
    });

    render(
      <MetricsProvider>
        <Dashboard />
      </MetricsProvider>
    );

    // Verify initial connection
    expect(global.WebSocket).toHaveBeenCalled();

    // Step 1: Simulate connection loss
    const closeEvent = new CloseEvent('close', { code: 1006, reason: 'Connection lost' });
    mockWebSocket.onclose(closeEvent);

    // Step 2: Verify reconnection attempt
    await waitFor(() => {
      expect(screen.getByText(/reconnecting/i)).toBeInTheDocument();
    });

    // Should attempt to reconnect
    await waitFor(() => {
      expect(global.WebSocket).toHaveBeenCalledTimes(2); // Initial + reconnect
    }, { timeout: 3000 });

    // Step 3: Simulate successful reconnection
    mockWebSocket.onopen();

    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument();
      expect(screen.queryByText(/reconnecting/i)).not.toBeInTheDocument();
    });

    // Step 4: Verify data resumes after reconnection
    const postReconnectUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'resilience-test-agent',
        timestamp: '2025-09-21T06:03:00Z',
        latency_ms: 180,
        cpu_usage_percent: 50
      }
    };

    const messageEvent = new MessageEvent('message', {
      data: JSON.stringify(postReconnectUpdate)
    });
    mockWebSocket.onmessage(messageEvent);

    await waitFor(() => {
      expect(screen.getByText('resilience-test-agent')).toBeInTheDocument();
      expect(screen.getByText('180ms')).toBeInTheDocument();
    });
  });

  it('should handle real-time data visualization updates', async () => {
    // This WILL FAIL until real-time charts are implemented

    // Setup dashboard with chart component
    const initialResponse = {
      metrics: [
        {
          agent_id: 'chart-agent',
          timestamp: '2025-09-21T06:00:00Z',
          latency_ms: 100,
          cpu_usage_percent: 30
        }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(initialResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showCharts={true} />
      </MetricsProvider>
    );

    // Verify initial chart renders
    await waitFor(() => {
      expect(screen.getByTestId('latency-chart')).toBeInTheDocument();
      expect(screen.getByTestId('cpu-chart')).toBeInTheDocument();
    });

    // Step 1: Send series of updates for chart animation
    const chartUpdates = [
      { latency_ms: 120, cpu_usage_percent: 35, timestamp: '2025-09-21T06:01:00Z' },
      { latency_ms: 140, cpu_usage_percent: 40, timestamp: '2025-09-21T06:02:00Z' },
      { latency_ms: 110, cpu_usage_percent: 32, timestamp: '2025-09-21T06:03:00Z' },
      { latency_ms: 160, cpu_usage_percent: 45, timestamp: '2025-09-21T06:04:00Z' }
    ];

    for (const [index, update] of chartUpdates.entries()) {
      const chartUpdate = {
        type: 'metric_update',
        data: {
          agent_id: 'chart-agent',
          ...update
        }
      };

      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(chartUpdate)
      });
      mockWebSocket.onmessage(messageEvent);

      // Allow time for chart animation
      await waitFor(() => {
        // Chart should show updated values
        const latencyChart = screen.getByTestId('latency-chart');
        expect(latencyChart).toHaveAttribute('data-current-value', update.latency_ms.toString());
      });
    }

    // Step 2: Verify chart shows historical trend
    const latencyChart = screen.getByTestId('latency-chart');
    const chartData = JSON.parse(latencyChart.getAttribute('data-series') || '[]');
    
    // Should have all data points for trend analysis
    expect(chartData.length).toBe(5); // Initial + 4 updates
    
    // Verify data point progression
    expect(chartData[0].latency_ms).toBe(100); // Initial
    expect(chartData[4].latency_ms).toBe(160); // Latest

    // Step 3: Verify real-time chart performance (no lag)
    const startTime = performance.now();
    
    const rapidUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'chart-agent',
        timestamp: '2025-09-21T06:05:00Z',
        latency_ms: 200,
        cpu_usage_percent: 60
      }
    };

    const rapidEvent = new MessageEvent('message', {
      data: JSON.stringify(rapidUpdate)
    });
    mockWebSocket.onmessage(rapidEvent);

    await waitFor(() => {
      const updatedChart = screen.getByTestId('latency-chart');
      expect(updatedChart).toHaveAttribute('data-current-value', '200');
    });

    const updateTime = performance.now() - startTime;
    // Chart should update within reasonable time (< 100ms)
    expect(updateTime).toBeLessThan(100);
  });
});

describe('Dashboard Real-time Updates Advanced Scenarios', () => {
  let mockWebSocket: any;
  let mockFetch: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch = vi.fn();
    global.fetch = mockFetch;
    
    mockWebSocket = {
      onopen: vi.fn(),
      onmessage: vi.fn(),
      onclose: vi.fn(),
      onerror: vi.fn(),
      send: vi.fn(),
      close: vi.fn(),
      readyState: 1,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    };
    
    (global.WebSocket as any).mockImplementation(() => mockWebSocket);
  });

  it('should handle real-time updates for multiple agent types simultaneously', async () => {
    // This WILL FAIL until multi-agent real-time handling is implemented

    const multiAgentResponse = {
      metrics: [
        { agent_id: 'web-agent-1', type: 'web', latency_ms: 150 },
        { agent_id: 'api-agent-1', type: 'api', latency_ms: 80 },
        { agent_id: 'ml-agent-1', type: 'ml', latency_ms: 300 }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(multiAgentResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard groupBy="type" />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('web-agent-1')).toBeInTheDocument();
      expect(screen.getByText('api-agent-1')).toBeInTheDocument();
      expect(screen.getByText('ml-agent-1')).toBeInTheDocument();
    });

    // Send simultaneous updates for different agent types
    const simultaneousUpdates = [
      {
        type: 'metric_update',
        data: { agent_id: 'web-agent-1', latency_ms: 200, timestamp: '2025-09-21T06:01:00Z' }
      },
      {
        type: 'metric_update', 
        data: { agent_id: 'api-agent-1', latency_ms: 120, timestamp: '2025-09-21T06:01:00Z' }
      },
      {
        type: 'metric_update',
        data: { agent_id: 'ml-agent-1', latency_ms: 450, timestamp: '2025-09-21T06:01:00Z' }
      }
    ];

    // Send all updates simultaneously
    simultaneousUpdates.forEach(update => {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(update)
      });
      mockWebSocket.onmessage(messageEvent);
    });

    // Verify all updates are applied correctly
    await waitFor(() => {
      expect(screen.getByText('200ms')).toBeInTheDocument(); // web-agent-1
      expect(screen.getByText('120ms')).toBeInTheDocument(); // api-agent-1
      expect(screen.getByText('450ms')).toBeInTheDocument(); // ml-agent-1
    });

    // Verify grouping by type still works with real-time updates
    expect(screen.getByText('Web Agents')).toBeInTheDocument();
    expect(screen.getByText('API Agents')).toBeInTheDocument();
    expect(screen.getByText('ML Agents')).toBeInTheDocument();
  });

  it('should handle real-time filtering and search with live updates', async () => {
    // This WILL FAIL until real-time filtering is implemented

    const searchableResponse = {
      metrics: [
        { agent_id: 'search-agent-prod', environment: 'production', latency_ms: 150 },
        { agent_id: 'search-agent-dev', environment: 'development', latency_ms: 100 },
        { agent_id: 'other-agent-prod', environment: 'production', latency_ms: 200 }
      ]
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(searchableResponse)
    });

    render(
      <MetricsProvider>
        <Dashboard showSearch={true} />
      </MetricsProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('search-agent-prod')).toBeInTheDocument();
      expect(screen.getByText('search-agent-dev')).toBeInTheDocument();
      expect(screen.getByText('other-agent-prod')).toBeInTheDocument();
    });

    // Apply search filter
    const searchInput = screen.getByPlaceholderText('Search agents...');
    fireEvent.change(searchInput, { target: { value: 'search-agent' } });

    await waitFor(() => {
      expect(screen.getByText('search-agent-prod')).toBeInTheDocument();
      expect(screen.getByText('search-agent-dev')).toBeInTheDocument();
      expect(screen.queryByText('other-agent-prod')).not.toBeInTheDocument();
    });

    // Send real-time update for filtered agent
    const filteredUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'search-agent-prod',
        latency_ms: 250,
        timestamp: '2025-09-21T06:01:00Z'
      }
    };

    const messageEvent = new MessageEvent('message', {
      data: JSON.stringify(filteredUpdate)
    });
    mockWebSocket.onmessage(messageEvent);

    // Verify update appears even with filter active
    await waitFor(() => {
      expect(screen.getByText('250ms')).toBeInTheDocument();
    });

    // Send update for non-filtered agent (should not appear)
    const nonFilteredUpdate = {
      type: 'metric_update',
      data: {
        agent_id: 'other-agent-prod',
        latency_ms: 350,
        timestamp: '2025-09-21T06:01:00Z'
      }
    };

    const nonFilteredEvent = new MessageEvent('message', {
      data: JSON.stringify(nonFilteredUpdate)
    });
    mockWebSocket.onmessage(nonFilteredEvent);

    // Should not show non-filtered agent updates
    expect(screen.queryByText('350ms')).not.toBeInTheDocument();
    expect(screen.queryByText('other-agent-prod')).not.toBeInTheDocument();
  });
});