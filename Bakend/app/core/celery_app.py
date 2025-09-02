from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "trading_backend",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.crypto_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    task_track_started=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "sync-crypto-data-hourly": {
        "task": "app.tasks.crypto_tasks.sync_cryptocurrency_data",
        "schedule": 3600.0,  # Run every hour
        "kwargs": {"limit": 200, "provider": "coingecko"}
    },
    "sync-top-crypto-frequent": {
        "task": "app.tasks.crypto_tasks.sync_cryptocurrency_data", 
        "schedule": 300.0,  # Run every 5 minutes
        "kwargs": {"limit": 50, "provider": "coingecko"}
    },
    "cleanup-old-price-history": {
        "task": "app.tasks.crypto_tasks.cleanup_old_price_history",
        "schedule": 86400.0,  # Run daily
        "kwargs": {"days_to_keep": 365}
    }
}

celery_app.conf.timezone = "UTC"