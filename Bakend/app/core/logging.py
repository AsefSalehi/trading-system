import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if available
        corr_id = correlation_id.get()
        if corr_id:
            log_entry["correlation_id"] = corr_id
            
        # Add extra fields
        if hasattr(record, 'extra') and record.extra:
            log_entry.update(record.extra)
            
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        corr_id = correlation_id.get()
        if corr_id:
            record.correlation_id = corr_id
        return True


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(settings.PROJECT_NAME)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Create console handler with JSON formatting for production
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Use JSON formatter in production, simple formatter in development
        if settings.ENVIRONMENT == "production":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        
        console_handler.setFormatter(formatter)
        console_handler.addFilter(CorrelationIdFilter())

        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def set_correlation_id(self, corr_id: str = None) -> str:
        """Set correlation ID for request tracking"""
        if not corr_id:
            corr_id = str(uuid.uuid4())
        correlation_id.set(corr_id)
        return corr_id

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return correlation_id.get()

    def info(self, message: str, extra: Dict[str, Any] = None, **kwargs):
        """Log info message with optional extra data"""
        self._log(logging.INFO, message, extra, **kwargs)

    def error(self, message: str, extra: Dict[str, Any] = None, **kwargs):
        """Log error message with optional extra data"""
        self._log(logging.ERROR, message, extra, **kwargs)

    def warning(self, message: str, extra: Dict[str, Any] = None, **kwargs):
        """Log warning message with optional extra data"""
        self._log(logging.WARNING, message, extra, **kwargs)

    def debug(self, message: str, extra: Dict[str, Any] = None, **kwargs):
        """Log debug message with optional extra data"""
        self._log(logging.DEBUG, message, extra, **kwargs)

    def _log(self, level: int, message: str, extra: Dict[str, Any] = None, **kwargs):
        """Internal logging method"""
        log_extra = extra or {}
        log_extra.update(kwargs)
        
        # Create a custom LogRecord to include extra data
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        record.extra = log_extra
        
        self.logger.handle(record)

    def log_api_request(self, method: str, path: str, status_code: int, 
                       duration_ms: float, user_id: Optional[int] = None):
        """Log API request with structured data"""
        self.info(
            f"{method} {path} - {status_code}",
            extra={
                "event_type": "api_request",
                "http_method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
            }
        )

    def log_authentication(self, username: str, success: bool, reason: str = None):
        """Log authentication attempts"""
        self.info(
            f"Authentication {'successful' if success else 'failed'} for {username}",
            extra={
                "event_type": "authentication",
                "username": username,
                "success": success,
                "reason": reason,
            }
        )

    def log_background_job(self, job_name: str, status: str, duration_ms: float = None,
                          result: Dict[str, Any] = None, error: str = None):
        """Log background job execution"""
        self.info(
            f"Background job {job_name} {status}",
            extra={
                "event_type": "background_job",
                "job_name": job_name,
                "status": status,
                "duration_ms": duration_ms,
                "result": result,
                "error": error,
            }
        )

    def log_database_operation(self, operation: str, table: str, duration_ms: float,
                              affected_rows: int = None):
        """Log database operations"""
        self.debug(
            f"Database {operation} on {table}",
            extra={
                "event_type": "database_operation",
                "operation": operation,
                "table": table,
                "duration_ms": duration_ms,
                "affected_rows": affected_rows,
            }
        )


logger = Logger()
