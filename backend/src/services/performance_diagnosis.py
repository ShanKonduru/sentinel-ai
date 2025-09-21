"""
Performance diagnosis service for Sentinel AI.

This service provides functionality for diagnosing performance issues,
identifying bottlenecks, and providing optimization recommendations.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case

from ..models import PerformanceMetric, AIAgent


class PerformanceIssueType(Enum):
    """Types of performance issues."""
    HIGH_LATENCY = "high_latency"
    LOW_THROUGHPUT = "low_throughput"
    HIGH_RESOURCE_USAGE = "high_resource_usage"
    MEMORY_LEAK = "memory_leak"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INTERMITTENT_ISSUES = "intermittent_issues"


class IssueSeverity(Enum):
    """Severity levels for performance issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceIssue:
    """Data class for performance issues."""
    agent_id: str
    agent_name: str
    issue_type: PerformanceIssueType
    severity: IssueSeverity
    title: str
    description: str
    current_value: float
    threshold_value: float
    recommendation: str
    detected_at: datetime
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int


@dataclass
class PerformanceSummary:
    """Data class for performance summary."""
    agent_id: str
    agent_name: str
    overall_health: str  # 'excellent', 'good', 'fair', 'poor', 'critical'
    latency_score: int  # 0-100
    throughput_score: int  # 0-100
    resource_efficiency_score: int  # 0-100
    reliability_score: int  # 0-100
    issues_count: int
    recommendations_count: int


class PerformanceDiagnosisService:
    """Service for diagnosing performance issues and providing recommendations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def diagnose_agent_performance(
        self,
        agent_id: str,
        hours: int = 24
    ) -> Tuple[PerformanceSummary, List[PerformanceIssue]]:
        """
        Comprehensive performance diagnosis for an agent.
        
        Args:
            agent_id: Agent ID to diagnose
            hours: Number of hours to analyze
            
        Returns:
            Tuple of (performance summary, list of issues)
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        # Get agent info
        agent = self.db.query(AIAgent).filter(AIAgent.agent_id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get performance metrics for the period
        metrics = self.db.query(PerformanceMetric).filter(
            and_(
                PerformanceMetric.agent_id == agent_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time
            )
        ).all()
        
        if not metrics:
            return PerformanceSummary(
                agent_id=agent_id,
                agent_name=agent.name,
                overall_health='unknown',
                latency_score=0,
                throughput_score=0,
                resource_efficiency_score=0,
                reliability_score=0,
                issues_count=0,
                recommendations_count=0
            ), []
        
        # Detect issues
        issues = []
        issues.extend(self._detect_latency_issues(agent, metrics))
        issues.extend(self._detect_throughput_issues(agent, metrics))
        issues.extend(self._detect_resource_issues(agent, metrics))
        issues.extend(self._detect_reliability_issues(agent, metrics))
        issues.extend(self._detect_performance_degradation(agent, metrics, start_time, end_time))
        
        # Calculate scores
        latency_score = self._calculate_latency_score(metrics)
        throughput_score = self._calculate_throughput_score(metrics)
        resource_score = self._calculate_resource_efficiency_score(metrics)
        reliability_score = self._calculate_reliability_score(metrics)
        
        # Determine overall health
        overall_score = (latency_score + throughput_score + resource_score + reliability_score) / 4
        overall_health = self._score_to_health_rating(overall_score)
        
        summary = PerformanceSummary(
            agent_id=agent_id,
            agent_name=agent.name,
            overall_health=overall_health,
            latency_score=latency_score,
            throughput_score=throughput_score,
            resource_efficiency_score=resource_score,
            reliability_score=reliability_score,
            issues_count=len(issues),
            recommendations_count=len([i for i in issues if i.recommendation])
        )
        
        return summary, issues
    
    def get_performance_recommendations(
        self,
        agent_id: str,
        days: int = 7
    ) -> List[Dict[str, any]]:
        """
        Get performance optimization recommendations for an agent.
        
        Args:
            agent_id: Agent ID to analyze
            days: Number of days to analyze
            
        Returns:
            List of recommendation dictionaries
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # Get performance summary
        summary, issues = self.diagnose_agent_performance(agent_id, hours=days*24)
        
        recommendations = []
        
        # General recommendations based on scores
        if summary.latency_score < 70:
            recommendations.append({
                'category': 'latency',
                'priority': 'high',
                'title': 'Optimize Response Latency',
                'description': 'Latency performance is below optimal levels',
                'actions': [
                    'Review model parameters and reduce complexity if possible',
                    'Implement response caching for repeated queries',
                    'Consider using faster hardware or optimized inference engines',
                    'Analyze request patterns for potential batching opportunities'
                ]
            })
        
        if summary.throughput_score < 70:
            recommendations.append({
                'category': 'throughput',
                'priority': 'high',
                'title': 'Improve Request Throughput',
                'description': 'Request processing throughput could be improved',
                'actions': [
                    'Implement request queuing and batch processing',
                    'Optimize concurrent request handling',
                    'Consider horizontal scaling or load balancing',
                    'Review resource allocation and scaling policies'
                ]
            })
        
        if summary.resource_efficiency_score < 70:
            recommendations.append({
                'category': 'resources',
                'priority': 'medium',
                'title': 'Optimize Resource Usage',
                'description': 'Resource utilization could be more efficient',
                'actions': [
                    'Monitor and optimize memory usage patterns',
                    'Review CPU utilization and adjust allocation',
                    'Implement resource pooling and reuse strategies',
                    'Consider auto-scaling based on demand'
                ]
            })
        
        if summary.reliability_score < 70:
            recommendations.append({
                'category': 'reliability',
                'priority': 'high',
                'title': 'Improve System Reliability',
                'description': 'System reliability needs attention',
                'actions': [
                    'Implement comprehensive error handling and retry logic',
                    'Add health checks and monitoring alerts',
                    'Review system dependencies and failure points',
                    'Implement circuit breaker patterns for external calls'
                ]
            })
        
        # Add specific recommendations from detected issues
        for issue in issues:
            if issue.severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]:
                recommendations.append({
                    'category': issue.issue_type.value,
                    'priority': issue.severity.value,
                    'title': issue.title,
                    'description': issue.description,
                    'actions': [issue.recommendation] if issue.recommendation else []
                })
        
        return recommendations
    
    def _detect_latency_issues(self, agent: AIAgent, metrics: List[PerformanceMetric]) -> List[PerformanceIssue]:
        """Detect latency-related performance issues."""
        issues = []
        
        latency_values = [m.latency_ms for m in metrics if m.latency_ms is not None]
        if not latency_values:
            return issues
        
        avg_latency = sum(latency_values) / len(latency_values)
        p95_latency = sorted(latency_values)[int(len(latency_values) * 0.95)]
        
        # High average latency
        if avg_latency > 2000:  # 2 seconds
            issues.append(PerformanceIssue(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                issue_type=PerformanceIssueType.HIGH_LATENCY,
                severity=IssueSeverity.HIGH,
                title="High Average Latency",
                description=f"Average latency ({avg_latency:.1f}ms) exceeds recommended threshold",
                current_value=avg_latency,
                threshold_value=2000,
                recommendation="Optimize model parameters, implement caching, or upgrade hardware",
                detected_at=datetime.now(timezone.utc),
                first_seen=min(m.timestamp for m in metrics if m.latency_ms and m.latency_ms > 2000),
                last_seen=max(m.timestamp for m in metrics if m.latency_ms and m.latency_ms > 2000),
                occurrence_count=len([l for l in latency_values if l > 2000])
            ))
        
        # High P95 latency
        if p95_latency > 5000:  # 5 seconds
            issues.append(PerformanceIssue(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                issue_type=PerformanceIssueType.HIGH_LATENCY,
                severity=IssueSeverity.CRITICAL,
                title="High P95 Latency",
                description=f"95th percentile latency ({p95_latency:.1f}ms) is critically high",
                current_value=p95_latency,
                threshold_value=5000,
                recommendation="Investigate and fix performance bottlenecks causing latency spikes",
                detected_at=datetime.now(timezone.utc),
                first_seen=min(m.timestamp for m in metrics),
                last_seen=max(m.timestamp for m in metrics),
                occurrence_count=len([l for l in latency_values if l > 5000])
            ))
        
        return issues
    
    def _detect_throughput_issues(self, agent: AIAgent, metrics: List[PerformanceMetric]) -> List[PerformanceIssue]:
        """Detect throughput-related performance issues."""
        issues = []
        
        throughput_values = [m.throughput_req_per_min for m in metrics if m.throughput_req_per_min is not None]
        if not throughput_values:
            return issues
        
        avg_throughput = sum(throughput_values) / len(throughput_values)
        
        # Low throughput
        if avg_throughput < 5:  # Less than 5 requests per minute
            issues.append(PerformanceIssue(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                issue_type=PerformanceIssueType.LOW_THROUGHPUT,
                severity=IssueSeverity.MEDIUM,
                title="Low Request Throughput",
                description=f"Average throughput ({avg_throughput:.1f} req/min) is below optimal levels",
                current_value=avg_throughput,
                threshold_value=5,
                recommendation="Implement request batching, optimize processing pipeline, or scale resources",
                detected_at=datetime.now(timezone.utc),
                first_seen=min(m.timestamp for m in metrics),
                last_seen=max(m.timestamp for m in metrics),
                occurrence_count=len([t for t in throughput_values if t < 5])
            ))
        
        return issues
    
    def _detect_resource_issues(self, agent: AIAgent, metrics: List[PerformanceMetric]) -> List[PerformanceIssue]:
        """Detect resource utilization issues."""
        issues = []
        
        # CPU usage issues
        cpu_values = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            max_cpu = max(cpu_values)
            
            if avg_cpu > 85:
                issues.append(PerformanceIssue(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    issue_type=PerformanceIssueType.HIGH_RESOURCE_USAGE,
                    severity=IssueSeverity.HIGH,
                    title="High CPU Usage",
                    description=f"Average CPU usage ({avg_cpu:.1f}%) is critically high",
                    current_value=avg_cpu,
                    threshold_value=85,
                    recommendation="Scale CPU resources or optimize computational workload",
                    detected_at=datetime.now(timezone.utc),
                    first_seen=min(m.timestamp for m in metrics if m.cpu_usage_percent and m.cpu_usage_percent > 85),
                    last_seen=max(m.timestamp for m in metrics if m.cpu_usage_percent and m.cpu_usage_percent > 85),
                    occurrence_count=len([c for c in cpu_values if c > 85])
                ))
        
        # Memory usage issues
        memory_values = [m.memory_usage_mb for m in metrics if m.memory_usage_mb is not None]
        if memory_values:
            memory_trend = self._calculate_trend(memory_values)
            if memory_trend > 20:  # 20% increase over time period
                issues.append(PerformanceIssue(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    issue_type=PerformanceIssueType.MEMORY_LEAK,
                    severity=IssueSeverity.HIGH,
                    title="Potential Memory Leak",
                    description=f"Memory usage shows increasing trend ({memory_trend:.1f}% growth)",
                    current_value=memory_values[-1],
                    threshold_value=memory_values[0] * 1.2,
                    recommendation="Investigate memory allocation patterns and fix potential memory leaks",
                    detected_at=datetime.now(timezone.utc),
                    first_seen=min(m.timestamp for m in metrics),
                    last_seen=max(m.timestamp for m in metrics),
                    occurrence_count=1
                ))
        
        return issues
    
    def _detect_reliability_issues(self, agent: AIAgent, metrics: List[PerformanceMetric]) -> List[PerformanceIssue]:
        """Detect reliability-related issues."""
        issues = []
        
        # Check for data gaps (potential downtime)
        if len(metrics) < 2:
            return issues
        
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        max_gap = timedelta(0)
        
        for i in range(1, len(sorted_metrics)):
            gap = sorted_metrics[i].timestamp - sorted_metrics[i-1].timestamp
            if gap > max_gap:
                max_gap = gap
        
        if max_gap > timedelta(hours=1):  # Gap larger than 1 hour
            issues.append(PerformanceIssue(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                issue_type=PerformanceIssueType.INTERMITTENT_ISSUES,
                severity=IssueSeverity.MEDIUM,
                title="Data Collection Gaps",
                description=f"Detected data gap of {max_gap.total_seconds()/3600:.1f} hours",
                current_value=max_gap.total_seconds()/3600,
                threshold_value=1,
                recommendation="Investigate agent connectivity and monitoring system reliability",
                detected_at=datetime.now(timezone.utc),
                first_seen=min(m.timestamp for m in metrics),
                last_seen=max(m.timestamp for m in metrics),
                occurrence_count=1
            ))
        
        return issues
    
    def _detect_performance_degradation(
        self, 
        agent: AIAgent, 
        metrics: List[PerformanceMetric], 
        start_time: datetime, 
        end_time: datetime
    ) -> List[PerformanceIssue]:
        """Detect performance degradation over time."""
        issues = []
        
        # Split metrics into first half and second half of the time period
        mid_time = start_time + (end_time - start_time) / 2
        
        first_half = [m for m in metrics if m.timestamp <= mid_time]
        second_half = [m for m in metrics if m.timestamp > mid_time]
        
        if len(first_half) < 2 or len(second_half) < 2:
            return issues
        
        # Compare latency between periods
        first_half_latency = [m.latency_ms for m in first_half if m.latency_ms is not None]
        second_half_latency = [m.latency_ms for m in second_half if m.latency_ms is not None]
        
        if first_half_latency and second_half_latency:
            first_avg = sum(first_half_latency) / len(first_half_latency)
            second_avg = sum(second_half_latency) / len(second_half_latency)
            
            if first_avg > 0:
                degradation = ((second_avg - first_avg) / first_avg) * 100
                
                if degradation > 30:  # 30% degradation
                    issues.append(PerformanceIssue(
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        issue_type=PerformanceIssueType.PERFORMANCE_DEGRADATION,
                        severity=IssueSeverity.HIGH,
                        title="Performance Degradation Detected",
                        description=f"Latency increased by {degradation:.1f}% over the analysis period",
                        current_value=second_avg,
                        threshold_value=first_avg * 1.3,
                        recommendation="Investigate system changes, resource constraints, or external dependencies",
                        detected_at=datetime.now(timezone.utc),
                        first_seen=mid_time,
                        last_seen=end_time,
                        occurrence_count=1
                    ))
        
        return issues
    
    def _calculate_latency_score(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate latency performance score (0-100)."""
        latency_values = [m.latency_ms for m in metrics if m.latency_ms is not None]
        if not latency_values:
            return 50  # Neutral score if no data
        
        avg_latency = sum(latency_values) / len(latency_values)
        
        # Score based on latency thresholds
        if avg_latency <= 100:
            return 100
        elif avg_latency <= 500:
            return 85
        elif avg_latency <= 1000:
            return 70
        elif avg_latency <= 2000:
            return 50
        elif avg_latency <= 5000:
            return 25
        else:
            return 0
    
    def _calculate_throughput_score(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate throughput performance score (0-100)."""
        throughput_values = [m.throughput_req_per_min for m in metrics if m.throughput_req_per_min is not None]
        if not throughput_values:
            return 50
        
        avg_throughput = sum(throughput_values) / len(throughput_values)
        
        # Score based on throughput thresholds
        if avg_throughput >= 60:
            return 100
        elif avg_throughput >= 30:
            return 85
        elif avg_throughput >= 15:
            return 70
        elif avg_throughput >= 5:
            return 50
        elif avg_throughput >= 1:
            return 25
        else:
            return 0
    
    def _calculate_resource_efficiency_score(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate resource efficiency score (0-100)."""
        cpu_values = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
        memory_values = [m.memory_usage_mb for m in metrics if m.memory_usage_mb is not None]
        
        scores = []
        
        # CPU efficiency score
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            if 50 <= avg_cpu <= 80:  # Optimal range
                scores.append(100)
            elif 30 <= avg_cpu < 50 or 80 < avg_cpu <= 90:
                scores.append(70)
            elif avg_cpu < 30 or avg_cpu > 90:
                scores.append(30)
        
        # Memory trend score (penalize increasing trends)
        if memory_values and len(memory_values) > 1:
            trend = self._calculate_trend(memory_values)
            if trend <= 0:  # Stable or decreasing
                scores.append(100)
            elif trend <= 10:
                scores.append(70)
            elif trend <= 20:
                scores.append(40)
            else:
                scores.append(10)
        
        return int(sum(scores) / len(scores)) if scores else 50
    
    def _calculate_reliability_score(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate reliability score based on data consistency (0-100)."""
        if len(metrics) < 2:
            return 50
        
        # Calculate expected vs actual data points
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        total_time = sorted_metrics[-1].timestamp - sorted_metrics[0].timestamp
        expected_points = max(1, total_time.total_seconds() / 300)  # Every 5 minutes
        actual_points = len(metrics)
        
        reliability_ratio = min(1.0, actual_points / expected_points)
        
        return int(reliability_ratio * 100)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend percentage over the values list."""
        if len(values) < 2:
            return 0
        
        first_third = values[:len(values)//3] if len(values) >= 3 else [values[0]]
        last_third = values[-len(values)//3:] if len(values) >= 3 else [values[-1]]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        if first_avg == 0:
            return 0
        
        return ((last_avg - first_avg) / first_avg) * 100
    
    def _score_to_health_rating(self, score: float) -> str:
        """Convert numeric score to health rating."""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'critical'