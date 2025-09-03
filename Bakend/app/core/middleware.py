import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and correlation ID tracking"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = logger.set_correlation_id()
        else:
            logger.set_correlation_id(correlation_id)

        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Extract user ID if available
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id

        # Log the request
        logger.log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id,
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.request_duration_sum = 0.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        self.request_count += 1
        self.request_duration_sum += duration

        # Store metrics in request state for Prometheus endpoint
        if not hasattr(request.app.state, "metrics"):
            request.app.state.metrics = {}
        
        metrics = request.app.state.metrics
        endpoint = f"{request.method}_{request.url.path}"
        
        if endpoint not in metrics:
            metrics[endpoint] = {"count": 0, "duration_sum": 0.0}
        
        metrics[endpoint]["count"] += 1
        metrics[endpoint]["duration_sum"] += duration

        return response