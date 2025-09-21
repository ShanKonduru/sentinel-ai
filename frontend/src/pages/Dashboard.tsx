import { useState, useEffect } from 'react';

interface Agent {
  agent_id: string;
  name: string;
  status: string;
  last_seen: string;
  total_metrics: number;
}

interface Metric {
  metric_id: string;
  agent_id: string;
  timestamp: string;
  latency_ms?: number;
  throughput_req_per_min?: number;
  cost_per_request?: number;
  cpu_usage_percent?: number;
  gpu_usage_percent?: number;
  memory_usage_mb?: number;
}

export const Dashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Mock data for now - will be replaced with actual API calls
        const mockAgents: Agent[] = [
          {
            agent_id: '550e8400-e29b-41d4-a716-446655440000',
            name: 'GPT-4 Agent',
            status: 'running',
            last_seen: new Date().toISOString(),
            total_metrics: 150
          },
          {
            agent_id: '550e8400-e29b-41d4-a716-446655440001',
            name: 'Claude Agent',
            status: 'running',
            last_seen: new Date().toISOString(),
            total_metrics: 89
          }
        ];

        const mockMetrics: Metric[] = [
          {
            metric_id: '123e4567-e89b-12d3-a456-426614174000',
            agent_id: '550e8400-e29b-41d4-a716-446655440000',
            timestamp: new Date().toISOString(),
            latency_ms: 120.5,
            throughput_req_per_min: 45.2,
            cost_per_request: 0.002,
            cpu_usage_percent: 75.3,
            gpu_usage_percent: 82.1,
            memory_usage_mb: 1024.5
          }
        ];

        setAgents(mockAgents);
        setMetrics(mockMetrics);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-md p-4 max-w-md">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-semibold text-gray-900">
            Sentinel AI Dashboard
          </h1>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
          <div className="py-4">
            {/* Metrics Summary Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">A</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Active Agents
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {agents.filter(a => a.status === 'running').length}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">M</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Metrics
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {agents.reduce((sum, agent) => sum + agent.total_metrics, 0)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">L</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Avg Latency
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {metrics.length > 0 
                            ? `${(metrics.reduce((sum, m) => sum + (m.latency_ms || 0), 0) / metrics.length).toFixed(1)}ms`
                            : 'N/A'
                          }
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">C</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          System Status
                        </dt>
                        <dd className="text-lg font-medium text-green-900">
                          Healthy
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Agents Overview */}
            <div className="mt-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Active Agents
                  </h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {agents.map((agent) => (
                      <div key={agent.agent_id} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-gray-900">
                            {agent.name}
                          </h4>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            agent.status === 'running' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {agent.status}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                          <p>Metrics: {agent.total_metrics}</p>
                          <p>Last seen: {new Date(agent.last_seen).toLocaleString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Metrics */}
            <div className="mt-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Recent Metrics
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Timestamp
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Agent
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Latency (ms)
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            CPU (%)
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Memory (MB)
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {metrics.map((metric) => {
                          const agent = agents.find(a => a.agent_id === metric.agent_id);
                          return (
                            <tr key={metric.metric_id}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {new Date(metric.timestamp).toLocaleString()}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {agent?.name || 'Unknown'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {metric.latency_ms?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {metric.cpu_usage_percent?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {metric.memory_usage_mb?.toFixed(1) || 'N/A'}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};