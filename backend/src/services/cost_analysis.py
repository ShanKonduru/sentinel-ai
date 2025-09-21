"""
Cost analysis service for Sentinel AI.

This service provides functionality for analyzing costs, budgets,
and cost optimization recommendations.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case

from ..models import PerformanceMetric, AIAgent


class CostPeriod(Enum):
    """Supported cost analysis periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CostBreakdown:
    """Data class for cost breakdown analysis."""
    agent_id: str
    agent_name: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    avg_cost_per_request: float
    total_requests: int
    cost_trend: str  # 'increasing', 'decreasing', 'stable'
    cost_efficiency: str  # 'excellent', 'good', 'fair', 'poor'


@dataclass
class CostAlert:
    """Data class for cost-related alerts."""
    agent_id: str
    agent_name: str
    alert_type: str  # 'budget_exceeded', 'cost_spike', 'efficiency_drop'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime


class CostAnalysisService:
    """Service for analyzing costs and generating cost insights."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def analyze_costs(
        self,
        agent_id: Optional[str] = None,
        period: CostPeriod = CostPeriod.DAILY,
        days: int = 7
    ) -> List[CostBreakdown]:
        """
        Analyze costs for agents over a specified period.
        
        Args:
            agent_id: Optional agent ID to filter by
            period: Analysis period granularity
            days: Number of days to analyze
            
        Returns:
            List of cost breakdowns
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # Determine grouping interval
        if period == CostPeriod.DAILY:
            date_trunc = 'day'
        elif period == CostPeriod.WEEKLY:
            date_trunc = 'week'
        else:  # MONTHLY
            date_trunc = 'month'
        
        # Build query
        query = self.db.query(
            PerformanceMetric.agent_id,
            AIAgent.name.label('agent_name'),
            func.date_trunc(date_trunc, PerformanceMetric.timestamp).label('period_start'),
            func.sum(PerformanceMetric.cost_per_request).label('total_cost'),
            func.avg(PerformanceMetric.cost_per_request).label('avg_cost_per_request'),
            func.count(PerformanceMetric.metric_id).label('total_requests')
        ).join(
            AIAgent, PerformanceMetric.agent_id == AIAgent.agent_id
        ).filter(
            and_(
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time,
                PerformanceMetric.cost_per_request.isnot(None)
            )
        )
        
        if agent_id:
            query = query.filter(PerformanceMetric.agent_id == agent_id)
        
        query = query.group_by(
            PerformanceMetric.agent_id,
            AIAgent.name,
            func.date_trunc(date_trunc, PerformanceMetric.timestamp)
        ).order_by(
            PerformanceMetric.agent_id,
            func.date_trunc(date_trunc, PerformanceMetric.timestamp)
        )
        
        results = []
        for row in query.all():
            period_start = row.period_start
            period_end = self._get_period_end(period_start, period)
            
            # Calculate cost trend and efficiency
            cost_trend = self._calculate_cost_trend(row.agent_id, period_start, period_end)
            cost_efficiency = self._calculate_cost_efficiency(row.avg_cost_per_request)
            
            results.append(CostBreakdown(
                agent_id=row.agent_id,
                agent_name=row.agent_name,
                period_start=period_start,
                period_end=period_end,
                total_cost=float(row.total_cost or 0),
                avg_cost_per_request=float(row.avg_cost_per_request or 0),
                total_requests=row.total_requests,
                cost_trend=cost_trend,
                cost_efficiency=cost_efficiency
            ))
        
        return results
    
    def get_cost_alerts(
        self,
        agent_id: Optional[str] = None,
        hours: int = 24
    ) -> List[CostAlert]:
        """
        Generate cost-related alerts for agents.
        
        Args:
            agent_id: Optional agent ID to filter by
            hours: Number of hours to look back for alerts
            
        Returns:
            List of cost alerts
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        alerts = []
        
        # Get agents to check
        agent_query = self.db.query(AIAgent)
        if agent_id:
            agent_query = agent_query.filter(AIAgent.agent_id == agent_id)
        
        agents = agent_query.all()
        
        for agent in agents:
            # Check for cost spikes (>50% increase from previous period)
            current_cost = self._get_period_cost(agent.agent_id, start_time, end_time)
            previous_start = start_time - timedelta(hours=hours)
            previous_cost = self._get_period_cost(agent.agent_id, previous_start, start_time)
            
            if previous_cost > 0 and current_cost > 0:
                cost_increase = ((current_cost - previous_cost) / previous_cost) * 100
                
                if cost_increase > 100:  # >100% increase
                    alerts.append(CostAlert(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        alert_type='cost_spike',
                        severity='critical',
                        message=f'Cost increased by {cost_increase:.1f}% in the last {hours} hours',
                        current_value=current_cost,
                        threshold_value=previous_cost * 2,
                        timestamp=end_time
                    ))
                elif cost_increase > 50:  # >50% increase
                    alerts.append(CostAlert(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        alert_type='cost_spike',
                        severity='high',
                        message=f'Cost increased by {cost_increase:.1f}% in the last {hours} hours',
                        current_value=current_cost,
                        threshold_value=previous_cost * 1.5,
                        timestamp=end_time
                    ))
            
            # Check for efficiency drops (cost per request increase)
            current_avg_cost = self._get_average_cost_per_request(agent.agent_id, start_time, end_time)
            previous_avg_cost = self._get_average_cost_per_request(agent.agent_id, previous_start, start_time)
            
            if previous_avg_cost > 0 and current_avg_cost > 0:
                efficiency_drop = ((current_avg_cost - previous_avg_cost) / previous_avg_cost) * 100
                
                if efficiency_drop > 25:  # >25% increase in cost per request
                    alerts.append(CostAlert(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        alert_type='efficiency_drop',
                        severity='medium',
                        message=f'Cost per request increased by {efficiency_drop:.1f}%',
                        current_value=current_avg_cost,
                        threshold_value=previous_avg_cost * 1.25,
                        timestamp=end_time
                    ))
        
        return alerts
    
    def get_cost_optimization_recommendations(
        self,
        agent_id: str,
        days: int = 7
    ) -> Dict[str, any]:
        """
        Generate cost optimization recommendations for an agent.
        
        Args:
            agent_id: Agent ID to analyze
            days: Number of days to analyze
            
        Returns:
            Dictionary with optimization recommendations
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # Get cost and performance metrics
        metrics = self.db.query(
            func.avg(PerformanceMetric.cost_per_request).label('avg_cost'),
            func.avg(PerformanceMetric.latency_ms).label('avg_latency'),
            func.avg(PerformanceMetric.throughput_req_per_min).label('avg_throughput'),
            func.avg(PerformanceMetric.cpu_usage_percent).label('avg_cpu'),
            func.avg(PerformanceMetric.memory_usage_mb).label('avg_memory'),
            func.sum(PerformanceMetric.cost_per_request).label('total_cost'),
            func.count(PerformanceMetric.metric_id).label('total_requests')
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time
            )
        ).first()
        
        if not metrics or metrics.total_requests == 0:
            return {
                'agent_id': agent_id,
                'recommendations': ['No data available for analysis'],
                'potential_savings': 0,
                'confidence': 'low'
            }
        
        recommendations = []
        potential_savings = 0
        confidence = 'medium'
        
        # Check for high cost per request
        if metrics.avg_cost and metrics.avg_cost > 0.01:  # Threshold: $0.01 per request
            recommendations.append(
                f"High cost per request ({metrics.avg_cost:.4f}). "
                "Consider optimizing model parameters or using a more efficient model."
            )
            potential_savings += metrics.total_cost * 0.2  # Assume 20% savings possible
        
        # Check for high latency with high cost
        if metrics.avg_latency and metrics.avg_latency > 1000 and metrics.avg_cost and metrics.avg_cost > 0.005:
            recommendations.append(
                f"High latency ({metrics.avg_latency:.1f}ms) combined with high cost. "
                "Consider caching strategies or model optimization."
            )
            potential_savings += metrics.total_cost * 0.15
        
        # Check for low resource utilization
        if metrics.avg_cpu and metrics.avg_cpu < 30:
            recommendations.append(
                f"Low CPU utilization ({metrics.avg_cpu:.1f}%). "
                "Consider consolidating workloads or using smaller instances."
            )
            potential_savings += metrics.total_cost * 0.1
        
        # Check for memory overprovisioning
        if metrics.avg_memory and metrics.avg_memory < 500:  # Less than 500MB average
            recommendations.append(
                "Low memory usage detected. Consider using instances with less memory allocation."
            )
            potential_savings += metrics.total_cost * 0.05
        
        # Check throughput efficiency
        if metrics.avg_throughput and metrics.avg_throughput < 10:  # Less than 10 requests per minute
            recommendations.append(
                f"Low throughput ({metrics.avg_throughput:.1f} req/min). "
                "Consider batch processing or request optimization."
            )
        
        if not recommendations:
            recommendations.append("No major optimization opportunities identified. Current performance appears efficient.")
            confidence = 'high'
        
        return {
            'agent_id': agent_id,
            'analysis_period_days': days,
            'current_total_cost': round(metrics.total_cost or 0, 4),
            'recommendations': recommendations,
            'potential_monthly_savings': round(potential_savings * 30 / days, 2),
            'confidence': confidence,
            'metrics_summary': {
                'avg_cost_per_request': round(metrics.avg_cost or 0, 6),
                'avg_latency_ms': round(metrics.avg_latency or 0, 1),
                'avg_throughput': round(metrics.avg_throughput or 0, 1),
                'avg_cpu_usage': round(metrics.avg_cpu or 0, 1),
                'avg_memory_mb': round(metrics.avg_memory or 0, 1),
                'total_requests': metrics.total_requests
            }
        }
    
    def _get_period_cost(self, agent_id: str, start_time: datetime, end_time: datetime) -> float:
        """Get total cost for an agent in a time period."""
        result = self.db.query(
            func.sum(PerformanceMetric.cost_per_request)
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time,
                PerformanceMetric.cost_per_request.isnot(None)
            )
        ).scalar()
        
        return float(result or 0)
    
    def _get_average_cost_per_request(self, agent_id: str, start_time: datetime, end_time: datetime) -> float:
        """Get average cost per request for an agent in a time period."""
        result = self.db.query(
            func.avg(PerformanceMetric.cost_per_request)
        ).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time,
                PerformanceMetric.cost_per_request.isnot(None)
            )
        ).scalar()
        
        return float(result or 0)
    
    def _calculate_cost_trend(self, agent_id: str, period_start: datetime, period_end: datetime) -> str:
        """Calculate cost trend for an agent in a period."""
        # Get current period cost
        current_cost = self._get_period_cost(agent_id, period_start, period_end)
        
        # Get previous period cost
        period_duration = period_end - period_start
        previous_start = period_start - period_duration
        previous_cost = self._get_period_cost(agent_id, previous_start, period_start)
        
        if previous_cost == 0 or current_cost == 0:
            return 'stable'
        
        change_percent = ((current_cost - previous_cost) / previous_cost) * 100
        
        if change_percent > 10:
            return 'increasing'
        elif change_percent < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_cost_efficiency(self, avg_cost_per_request: float) -> str:
        """Calculate cost efficiency rating based on cost per request."""
        if avg_cost_per_request is None or avg_cost_per_request <= 0:
            return 'unknown'
        
        # Thresholds for cost efficiency (these would be configurable in practice)
        if avg_cost_per_request <= 0.001:
            return 'excellent'
        elif avg_cost_per_request <= 0.005:
            return 'good'
        elif avg_cost_per_request <= 0.01:
            return 'fair'
        else:
            return 'poor'
    
    def _get_period_end(self, period_start: datetime, period: CostPeriod) -> datetime:
        """Calculate the end time for a given period start."""
        if period == CostPeriod.DAILY:
            return period_start + timedelta(days=1)
        elif period == CostPeriod.WEEKLY:
            return period_start + timedelta(weeks=1)
        elif period == CostPeriod.MONTHLY:
            return period_start + timedelta(days=30)  # Approximate
        else:
            return period_start + timedelta(days=1)