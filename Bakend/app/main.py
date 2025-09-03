from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import logger
from app.core.redis import redis_client
from app.core.middleware import LoggingMiddleware, MetricsMiddleware
from app.core.metrics import get_metrics, get_health_metrics

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Set up CORS - More permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.devinapps\.com)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Trading Backend API")
    # Initialize Redis connection
    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Trading Backend API")
    # Close Redis connection
    await redis_client.disconnect()


@app.get("/")
async def root():
    return {
        "message": "Trading Backend API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return get_health_metrics()


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()
