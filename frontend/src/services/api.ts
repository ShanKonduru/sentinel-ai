/**
 * API service for communicating with Sentinel AI backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';
const DATA_API_BASE_URL = process.env.REACT_APP_DATA_API_URL || 'http://localhost:5001/api/v1';

export interface Agent {
  agent_id: string;
  name: string;
  description?: string;
  status: 'running' | 'stopped' | 'error' | 'unknown';
  created_at: string;
  last_seen?: string;
  agent_metadata?: Record<string, any>;
  total_metrics?: number;
  latest_metric_timestamp?: string;
}

export interface Metric {
  metric_id: string;
  agent_id: string;
  timestamp: string;
  latency_ms?: number;
  throughput_req_per_min?: number;
  cost_per_request?: number;
  cpu_usage_percent?: number;
  gpu_usage_percent?: number;
  memory_usage_mb?: number;
  custom_metrics?: Record<string, any>;
}

export interface MetricsSubmission {
  agent_id: string;
  timestamp: string;
  latency_ms?: number;
  throughput_req_per_min?: number;
  cost_per_request?: number;
  cpu_usage_percent?: number;
  gpu_usage_percent?: number;
  memory_usage_mb?: number;
  custom_metrics?: Record<string, any>;
}

class ApiService {
  private async request<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Metrics Collection API
  async submitMetrics(metrics: MetricsSubmission): Promise<{ success: boolean; message: string; metric_id: string }> {
    return this.request(`${API_BASE_URL}/metrics`, {
      method: 'POST',
      body: JSON.stringify(metrics),
    });
  }

  async getMetricsHealth(): Promise<{ status: string; timestamp: string; version: string }> {
    return this.request(`${API_BASE_URL}/health`);
  }

  // Data Retrieval API
  async getAgents(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ agents: Agent[]; total: number; limit: number; offset: number }> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = `${DATA_API_BASE_URL}/agents${queryParams.toString() ? `?${queryParams}` : ''}`;
    return this.request(url);
  }

  async getAgent(agentId: string): Promise<{ agent: Agent }> {
    return this.request(`${DATA_API_BASE_URL}/agents/${agentId}`);
  }

  async getMetrics(params?: {
    agent_id?: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
    offset?: number;
    aggregate?: string;
  }): Promise<{ metrics: Metric[]; total: number; limit: number; offset: number }> {
    const queryParams = new URLSearchParams();
    if (params?.agent_id) queryParams.append('agent_id', params.agent_id);
    if (params?.start_time) queryParams.append('start_time', params.start_time);
    if (params?.end_time) queryParams.append('end_time', params.end_time);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.aggregate) queryParams.append('aggregate', params.aggregate);

    const url = `${DATA_API_BASE_URL}/metrics${queryParams.toString() ? `?${queryParams}` : ''}`;
    return this.request(url);
  }

  async exportMetrics(params?: {
    agent_id?: string;
    start_time?: string;
    end_time?: string;
    format?: 'json' | 'csv';
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    if (params?.agent_id) queryParams.append('agent_id', params.agent_id);
    if (params?.start_time) queryParams.append('start_time', params.start_time);
    if (params?.end_time) queryParams.append('end_time', params.end_time);
    if (params?.format) queryParams.append('format', params.format);

    const url = `${DATA_API_BASE_URL}/export${queryParams.toString() ? `?${queryParams}` : ''}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    
    return response.blob();
  }

  async getDataHealth(): Promise<{ status: string; timestamp: string; version: string; database: { connected: boolean } }> {
    return this.request(`${DATA_API_BASE_URL}/health`);
  }
}

export const apiService = new ApiService();
export default apiService;