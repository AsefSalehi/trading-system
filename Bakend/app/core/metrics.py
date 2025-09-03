from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

BACKGROUND_JOBS_TOTAL = Counter(
    'background_jobs_total',
    'Total background jobs executed',
    ['job_name', 'status']
)

BACKGROUND_JOB_DURATION = Histogram(
    'background_job_duration_seconds',
    'Background job duration in seconds',
    ['job_name']
)

DATABASE_OPERATIONS_TOTAL = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table']
)

DATABASE_OPERATION_DURATION = Histogram(
    'database_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table']
)

AUTHENTICATION_ATTEMPTS_TOTAL = Counter(
    'authentication_attempts_total',
    'Total authentication attempts',
    ['result']
)

RISK_ASSESSMENTS_TOTAL = Counter(
    'risk_assessments_total',
    'Total risk assessments performed'
)

ACTIVE_ALERTS = Gauge(
    'active_risk_alerts',
    'Number of active risk alerts',
    ['severity']
)


class MetricsCollector:
    """Centralized metrics collection"""

    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    @staticmethod
    def record_background_job(job_name: str, status: str, duration: float = None):
        """Record background job metrics"""
        BACKGROUND_JOBS_TOTAL.labels(
            job_name=job_name,
            status=status
        ).inc()
        
        if duration is not None:
            BACKGROUND_JOB_DURATION.labels(job_name=job_name).observe(duration)

    @staticmethod
    def record_database_operation(operation: str, table: str, duration: float):
        """Record database operation metrics"""
        DATABASE_OPERATIONS_TOTAL.labels(
            operation=operation,
            table=table
        ).inc()
        
        DATABASE_OPERATION_DURATION.labels(
            operation=operation,
            table=table
        ).observe(duration)

    @staticmethod
    def record_authentication(success: bool):
        """Record authentication attempt"""
        result = "success" if success else "failure"
        AUTHENTICATION_ATTEMPTS_TOTAL.labels(result=result).inc()

    @staticmethod
    def record_risk_assessment():
        """Record risk assessment"""
        RISK_ASSESSMENTS_TOTAL.inc()

    @staticmethod
    def set_active_alerts(severity: str, count: int):
        """Set active alerts gauge"""
        ACTIVE_ALERTS.labels(severity=severity).set(count)

    @staticmethod
    def increment_active_connections():
        """Increment active connections"""
        ACTIVE_CONNECTIONS.inc()

    @staticmethod
    def decrement_active_connections():
        """Decrement active connections"""
        ACTIVE_CONNECTIONS.dec()


def get_metrics() -> Response:
    """Generate Prometheus metrics response"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def get_health_metrics() -> Dict[str, Any]:
    """Get application health metrics"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "metrics": {
            "total_requests": REQUEST_COUNT._value.sum(),
            "active_connections": ACTIVE_CONNECTIONS._value.get(),
            "total_background_jobs": BACKGROUND_JOBS_TOTAL._value.sum(),
            "total_risk_assessments": RISK_ASSESSMENTS_TOTAL._value.get(),
        }
    }