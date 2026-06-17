import hmac
import hashlib
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Request, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database import get_db
from app.config import settings
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review import Review
from app.models.enums import PRStatus, ReviewStatus
from app.schemas.webhook import GitHubWebhookPayload, WebhookResponse
from app.exceptions import HTTP400
from app.tasks.review_tasks import run_review_pipeline


router = APIRouter(prefix="/api/webhook", tags=["webhook"])


def validate_webhook_signature(
    payload_body: bytes,
    signature_header: str
) -> None:
    if not signature_header:
        raise HTTP400("Missing webhook signature header")

    if not signature_header.startswith("sha256="):
        raise HTTP400("Invalid signature format")

    expected_signature = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    actual_signature = signature_header[7:]

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTP400("Webhook signature validation failed")


def parse_github_datetime(dt_str: str) -> datetime | None:
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


@router.post("", response_model=WebhookResponse, status_code=202)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> WebhookResponse:
    # Read raw body for signature validation
    payload_body = await request.body()

    # Step 1 — Validate signature
    try:
        validate_webhook_signature(payload_body, x_hub_signature_256)
    except HTTP400 as e:
        logger.warning(f"Webhook signature validation failed: {e.detail}")
        raise

    # Step 2 — Parse payload
    try:
        payload_dict = json.loads(payload_body)
        payload = GitHubWebhookPayload(**payload_dict)
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {str(e)}")
        raise HTTP400("Invalid webhook payload")

    # Step 3 — Filter events
    if x_github_event != "pull_request":
        logger.info(f"Ignoring event type: {x_github_event}")
        return WebhookResponse(message="Event ignored")

    if payload.action != "opened":
        logger.info(f"Ignoring PR action: {payload.action}")
        return WebhookResponse(message="Action ignored")

    if not payload.pull_request or not payload.repository:
        raise HTTP400("Missing pull request or repository data")

    # Step 4 — Find repository in DB
    repo_full_name = payload.repository.full_name
    pr_number = payload.pull_request.number

    result = await db.execute(
        select(Repository).where(
            Repository.full_name == repo_full_name,
            Repository.is_active == True
        )
    )
    repository = result.scalar_one_or_none()

    if not repository:
        logger.info(
            f"Repository {repo_full_name} not connected — ignoring webhook"
        )
        return WebhookResponse(message="Repository not connected")

    # Step 5 — Create PullRequest row
    pr_created_at = parse_github_datetime(payload.pull_request.created_at)

    pull_request = PullRequest(
        repository_id=repository.id,
        pr_number=pr_number,
        title=payload.pull_request.title,
        description=payload.pull_request.body,
        author=payload.pull_request.user.login,
        base_branch=payload.pull_request.base.get("ref", ""),
        head_branch=payload.pull_request.head.get("ref", ""),
        diff_url=payload.pull_request.diff_url,
        status=PRStatus.open.value,
        pr_created_at=pr_created_at
    )
    db.add(pull_request)
    await db.flush()

    # Step 6 — Create Review row
    review = Review(
        pull_request_id=pull_request.id,
        status=ReviewStatus.pending.value,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    logger.info(
        f"Created review {review.id} for PR #{pr_number} "
        f"in {repo_full_name}"
    )

    # Step 7 — Enqueue Celery task
    run_review_pipeline.delay(str(review.id))

    logger.info(f"Review {review.id} enqueued for processing")

    return WebhookResponse(
        message="Review started",
        review_id=str(review.id)
    )