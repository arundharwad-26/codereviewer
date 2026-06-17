from celery import Celery
from app.config import settings


# Create Celery instance
celery_app = Celery(
    "codereviewer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Retries
    task_max_retries=3,
    task_default_retry_delay=60,

    # Result expiry
    result_expires=3600,

    # Routes
    task_routes={
        "app.tasks.review_tasks.run_review_pipeline": {
            "queue": "reviews"
        }
    }
)

# Auto discover tasks
celery_app.autodiscover_tasks(["app.tasks"])