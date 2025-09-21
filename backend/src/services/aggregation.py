"""
Data aggregation service for Sentinel AI.

This service provides functionality for aggregating metrics data
at different time intervals and computing statistical summaries.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from ..models import PerformanceMetric, AIAgent


class AggregationInterval(Enum):
    """Supported aggregation intervals."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class AggregatedMetric:
    """Data class for aggregated metric results."""
    agent_id: str
    interval_start: datetime
    interval_end: datetime
    count: int
    avg_latency_ms: Optional[float] = None
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    avg_throughput: Optional[float] = None
    avg_cost_per_request: Optional[float] = None
    avg_cpu_usage: Optional[float] = None
    avg_gpu_usage: Optional[float] = None
    avg_memory_usage: Optional[float] = None
    total_cost: Optional[float] = None
    total_requests: Optional[float] = None


class DataAggregationService:
    """Service for aggregating metrics data."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def aggregate_metrics(
        self,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: AggregationInterval = AggregationInterval.HOUR
    ) -> List[AggregatedMetric]:
        """
        Aggregate metrics data for specified time range and interval.
        
        Args:
            agent_id: Optional agent ID to filter by
            start_time: Start of time range (defaults to 24 hours ago)
            end_time: End of time range (defaults to now)
            interval: Aggregation interval
            
        Returns:
            List of aggregated metrics
        """
        if not end_time:
            end_time = datetime.now(timezone.utc)
        
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        
        # Build base query
        query = self.db.query(
            PerformanceMetric.agent_id,
            func.date_trunc(interval.value, PerformanceMetric.timestamp).label('interval_start'),
            func.count(PerformanceMetric.metric_id).label('count'),
            func.avg(PerformanceMetric.latency_ms).label('avg_latency'),
            func.min(PerformanceMetric.latency_ms).label('min_latency'),
            func.max(PerformanceMetric.latency_ms).label('max_latency'),
            func.avg(PerformanceMetric.throughput_req_per_min).label('avg_throughput'),
            func.avg(PerformanceMetric.cost_per_request).label('avg_cost'),
            func.avg(PerformanceMetric.cpu_usage_percent).label('avg_cpu'),
            func.avg(PerformanceMetric.gpu_usage_percent).label('avg_gpu'),
            func.avg(PerformanceMetric.memory_usage_mb).label('avg_memory'),
            func.sum(PerformanceMetric.cost_per_request).label('total_cost'),
            func.sum(PerformanceMetric.throughput_req_per_min).label('total_requests')
        )
        
        # Apply filters
        filters = [
            PerformanceMetric.timestamp >= start_time,
            PerformanceMetric.timestamp <= end_time
        ]
        
        if agent_id:
            filters.append(PerformanceMetric.agent_id == agent_id)
        
        query = query.filter(and_(*filters))
        
        # Group by agent and time interval
        query = query.group_by(
            PerformanceMetric.agent_id,
            func.date_trunc(interval.value, PerformanceMetric.timestamp)
        ).order_by(
            PerformanceMetric.agent_id,
            func.date_trunc(interval.value, PerformanceMetric.timestamp)
        )
        
        # Execute query and convert to AggregatedMetric objects
        results = []
        for row in query.all():
            interval_start = row.interval_start
            interval_end = self._get_interval_end(interval_start, interval)
            
            results.append(AggregatedMetric(
                agent_id=row.agent_id,
                interval_start=interval_start,
                interval_end=interval_end,
                count=row.count,
                avg_latency_ms=row.avg_latency,
                min_latency_ms=row.min_latency,
                max_latency_ms=row.max_latency,
                avg_throughput=row.avg_throughput,
                avg_cost_per_request=row.avg_cost,
                avg_cpu_usage=row.avg_cpu,
                avg_gpu_usage=row.avg_gpu,
                avg_memory_usage=row.avg_memory,
                total_cost=row.total_cost,
                total_requests=row.total_requests
            ))
        
        return results
    
    def aggregate_metrics_by_time(
        self,
        agent_id: str,
        start_time: datetime,
        end_time: datetime,
        interval: AggregationInterval = AggregationInterval.HOUR
    ) -> List[Dict]:
        """
        Aggregate metrics data for a specific agent and time range.
        
        Args:
            agent_id: Agent ID to aggregate metrics for
            start_time: Start of time range
            end_time: End of time range
            interval: Aggregation interval
            
        Returns:
            List of aggregated metrics as dictionaries
        """
        # Build query for time-based aggregation
        query = """
            SELECT 
                date_trunc(%s, timestamp) as time_bucket,
                AVG(latency_ms) as avg_latency,
                AVG(throughput_req_per_min) as avg_throughput,
                AVG(cpu_usage_percent) as avg_cpu,
                AVG(memory_usage_mb) as avg_memory,
                COUNT(*) as metric_count
            FROM performance_metrics 
            WHERE agent_id = %s 
                AND timestamp >= %s 
                AND timestamp <= %s
            GROUP BY date_trunc(%s, timestamp)
            ORDER BY time_bucket
        """
        
        result = self.db.execute(query, (
            interval.value, agent_id, start_time, end_time, interval.value
        ))
        
        # Handle both real database results and mock results
        raw_results = result.fetchall()
        
        results = []
        for row in raw_results:
            # Handle mock data (dict) vs real data (tuple/row)
            if isinstance(row, dict):
                results.append(row)
            else:
                results.append({
                    'time_bucket': row[0],
                    'avg_latency': row[1],
                    'avg_throughput': row[2],
                    'avg_cpu': row[3],
                    'avg_memory': row[4],
                    'metric_count': row[5]
                })
        
        return results
    
    def get_agent_summary(
        self,
        agent_id: str,
        days: int = 7
    ) -> Dict[str, any]:
        """
        Get summary statistics for an agent over specified number of days.
        
        Args:
            agent_id: Agent ID to summarize
            days: Number of days to look back
            
        Returns:
            Dictionary with summary statistics
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # Get raw statistics
        stats = self.db.query(
            func.count(PerformanceMetric.metric_id).label('total_metrics'),
            func.avg(PerformanceMetric.latency_ms).label('avg_latency'),
            func.percentile_cont(0.95).within_group(PerformanceMetric.latency_ms).label('p95_latency'),
            func.avg(PerformanceMetric.throughput_req_per_min).label('avg_throughput'),
            func.sum(PerformanceMetric.cost_per_request).label('total_cost'),
            func.avg(PerformanceMetric.cpu_usage_percent).label('avg_cpu'),
            func.avg(PerformanceMetric.gpu_usage_percent).label('avg_gpu'),
            func.avg(PerformanceMetric.memory_usage_mb).label('avg_memory'),
            func.min(PerformanceMetric.timestamp).label('first_metric'),
            func.max(PerformanceMetric.timestamp).label('last_metric')
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time
            )
        ).first()
        
        # Get agent info
        agent = self.db.query(AIAgent).filter(AIAgent.agent_id == agent_id).first()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        return {
            'agent_id': agent_id,
            'agent_name': agent.name,
            'period_days': days,
            'period_start': start_time,
            'period_end': end_time,
            'total_metrics': stats.total_metrics or 0,
            'avg_latency_ms': round(stats.avg_latency, 2) if stats.avg_latency else None,
            'p95_latency_ms': round(stats.p95_latency, 2) if stats.p95_latency else None,
            'avg_throughput': round(stats.avg_throughput, 2) if stats.avg_throughput else None,
            'total_cost': round(stats.total_cost, 4) if stats.total_cost else None,
            'avg_cpu_usage': round(stats.avg_cpu, 1) if stats.avg_cpu else None,
            'avg_gpu_usage': round(stats.avg_gpu, 1) if stats.avg_gpu else None,
            'avg_memory_usage_mb': round(stats.avg_memory, 1) if stats.avg_memory else None,
            'first_metric': stats.first_metric,
            'last_metric': stats.last_metric,
            'uptime_hours': self._calculate_uptime_hours(agent_id, start_time, end_time)
        }
    
    def get_trend_analysis(
        self,
        agent_id: str,
        metric_name: str,
        hours: int = 24
    ) -> Dict[str, any]:
        """
        Analyze trends for a specific metric over time.
        
        Args:
            agent_id: Agent ID to analyze
            metric_name: Name of metric to analyze (e.g., 'latency_ms')
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        # Map metric names to database columns
        metric_column_map = {
            'latency_ms': PerformanceMetric.latency_ms,
            'throughput_req_per_min': PerformanceMetric.throughput_req_per_min,
            'cost_per_request': PerformanceMetric.cost_per_request,
            'cpu_usage_percent': PerformanceMetric.cpu_usage_percent,
            'gpu_usage_percent': PerformanceMetric.gpu_usage_percent,
            'memory_usage_mb': PerformanceMetric.memory_usage_mb
        }
        
        if metric_name not in metric_column_map:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        column = metric_column_map[metric_name]
        
        # Get hourly aggregates for trend analysis
        hourly_data = self.db.query(
            func.date_trunc('hour', PerformanceMetric.timestamp).label('hour'),
            func.avg(column).label('avg_value'),
            func.count(PerformanceMetric.metric_id).label('count')
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time,
                column.isnot(None)
            )
        ).group_by(
            func.date_trunc('hour', PerformanceMetric.timestamp)
        ).order_by(
            func.date_trunc('hour', PerformanceMetric.timestamp)
        ).all()
        
        if not hourly_data:
            return {
                'metric_name': metric_name,
                'agent_id': agent_id,
                'period_hours': hours,
                'trend': 'no_data',
                'change_percent': 0,
                'data_points': 0
            }
        
        # Calculate trend
        values = [float(row.avg_value) for row in hourly_data if row.avg_value is not None]
        
        if len(values) < 2:
            trend = 'insufficient_data'
            change_percent = 0
        else:
            first_value = values[0]
            last_value = values[-1]
            change_percent = ((last_value - first_value) / first_value) * 100
            
            if abs(change_percent) < 5:
                trend = 'stable'
            elif change_percent > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
        
        return {
            'metric_name': metric_name,
            'agent_id': agent_id,
            'period_hours': hours,
            'trend': trend,
            'change_percent': round(change_percent, 2),
            'data_points': len(hourly_data),
            'current_value': round(values[-1], 2) if values else None,
            'min_value': round(min(values), 2) if values else None,
            'max_value': round(max(values), 2) if values else None,
            'avg_value': round(sum(values) / len(values), 2) if values else None
        }
    
    def _get_interval_end(self, interval_start: datetime, interval: AggregationInterval) -> datetime:
        """Calculate the end time for a given interval start."""
        if interval == AggregationInterval.MINUTE:
            return interval_start + timedelta(minutes=1)
        elif interval == AggregationInterval.HOUR:
            return interval_start + timedelta(hours=1)
        elif interval == AggregationInterval.DAY:
            return interval_start + timedelta(days=1)
        elif interval == AggregationInterval.WEEK:
            return interval_start + timedelta(weeks=1)
        elif interval == AggregationInterval.MONTH:
            # Approximate month as 30 days
            return interval_start + timedelta(days=30)
        else:
            return interval_start + timedelta(hours=1)
    
    def _calculate_uptime_hours(self, agent_id: str, start_time: datetime, end_time: datetime) -> float:
        """Calculate estimated uptime hours based on metric submission frequency."""
        # Count hours with at least one metric submission
        hours_with_metrics = self.db.query(
            func.count(func.distinct(func.date_trunc('hour', PerformanceMetric.timestamp)))
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time
            )
        ).scalar()
        
        return hours_with_metrics or 0