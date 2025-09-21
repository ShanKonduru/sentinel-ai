import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Progress, Spin, Alert } from 'antd';
import { 
  DashboardOutlined, 
  RocketOutlined, 
  ClockCircleOutlined,
  TrophyOutlined,
  WarningOutlined 
} from '@ant-design/icons';
import { formatDistanceToNow } from 'date-fns';

export interface MetricsSummary {
  totalAgents: number;
  activeAgents: number;
  avgLatency: number;
  avgThroughput: number;
  avgCost: number;
  reliabilityScore: number;
  lastUpdated: string;
  totalSessions: number;
}

interface MetricsSummaryProps {
  summary?: MetricsSummary;
  loading?: boolean;
  error?: string;
}

const MetricsSummaryCards: React.FC<MetricsSummaryProps> = ({ 
  summary, 
  loading = false, 
  error 
}) => {
  if (loading) {
    return (
      <Card>
        <div className="flex justify-center items-center h-32">
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error Loading Metrics"
        description={error}
        type="error"
        showIcon
      />
    );
  }

  if (!summary) {
    return (
      <Alert
        message="No Data Available"
        description="No metrics data available to display"
        type="info"
        showIcon
      />
    );
  }

  const getReliabilityColor = (score: number) => {
    if (score >= 95) return '#52c41a'; // green
    if (score >= 90) return '#faad14'; // yellow
    return '#ff4d4f'; // red
  };

  const getLatencyColor = (latency: number) => {
    if (latency <= 100) return '#52c41a'; // green
    if (latency <= 500) return '#faad14'; // yellow
    return '#ff4d4f'; // red
  };

  return (
    <Row gutter={[16, 16]}>
      {/* Total Agents */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Total Agents"
            value={summary.totalAgents}
            prefix={<DashboardOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
          <div className="mt-2 text-sm text-gray-500">
            {summary.activeAgents} active
          </div>
        </Card>
      </Col>

      {/* Active Sessions */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Total Sessions"
            value={summary.totalSessions}
            prefix={<RocketOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
          <div className="mt-2 text-sm text-gray-500">
            {((summary.activeAgents / summary.totalAgents) * 100).toFixed(1)}% agents active
          </div>
        </Card>
      </Col>

      {/* Average Latency */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Avg Latency"
            value={summary.avgLatency}
            suffix="ms"
            prefix={<ClockCircleOutlined />}
            valueStyle={{ color: getLatencyColor(summary.avgLatency) }}
          />
          <div className="mt-2">
            <Progress
              percent={Math.min((summary.avgLatency / 1000) * 100, 100)}
              size="small"
              strokeColor={getLatencyColor(summary.avgLatency)}
              showInfo={false}
            />
          </div>
        </Card>
      </Col>

      {/* Reliability Score */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Reliability"
            value={summary.reliabilityScore}
            suffix="%"
            prefix={<TrophyOutlined />}
            valueStyle={{ color: getReliabilityColor(summary.reliabilityScore) }}
          />
          <div className="mt-2">
            <Progress
              percent={summary.reliabilityScore}
              size="small"
              strokeColor={getReliabilityColor(summary.reliabilityScore)}
              showInfo={false}
            />
          </div>
        </Card>
      </Col>

      {/* Throughput */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Avg Throughput"
            value={summary.avgThroughput}
            suffix="req/s"
            valueStyle={{ color: '#13c2c2' }}
          />
        </Card>
      </Col>

      {/* Cost */}
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="Avg Cost"
            value={summary.avgCost}
            prefix="$"
            precision={4}
            valueStyle={{ color: '#eb2f96' }}
          />
        </Card>
      </Col>

      {/* Last Updated */}
      <Col xs={24} sm={12} lg={12}>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500 mb-1">Last Updated</div>
              <div className="text-lg font-medium">
                {formatDistanceToNow(new Date(summary.lastUpdated), { addSuffix: true })}
              </div>
            </div>
            <div className="text-green-500">
              <DashboardOutlined style={{ fontSize: '24px' }} />
            </div>
          </div>
        </Card>
      </Col>
    </Row>
  );
};

export default MetricsSummaryCards;