import asyncio
import uuid
from loguru import logger
from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal


@celery_app.task(
    name="app.tasks.review_tasks.run_review_pipeline",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def run_review_pipeline(self, review_id: str) -> dict:
    """
    Celery task — entry point for the review pipeline.
    """
    logger.info(f"Task received for review {review_id}")

    # Create new event loop for Windows compatibility
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run():
        async with AsyncSessionLocal() as session:
            try:
                from app.agents.orchestrator import run_pipeline
                await run_pipeline(
                    review_id=uuid.UUID(review_id),
                    session=session
                )
                return {"status": "completed", "review_id": review_id}

            except Exception as e:
                logger.error(
                    f"Pipeline failed for review {review_id}: {str(e)}"
                )
                from app.agents.orchestrator import mark_failed
                await mark_failed(
                    review_id=uuid.UUID(review_id),
                    session=session,
                    error_message=str(e)
                )
                try:
                    raise self.retry(exc=e)
                except self.MaxRetriesExceededError:
                    logger.error(
                        f"Max retries exceeded for review {review_id}"
                    )
                    return {
                        "status": "failed",
                        "review_id": review_id,
                        "error": str(e)
                    }

    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()