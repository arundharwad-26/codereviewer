import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from loguru import logger

from app.database import get_db
from app.models.user import User
from app.models.review import Review
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_comment import ReviewComment
from app.models.enums import ReviewStatus
from app.schemas.reviews import (
    ReviewListResponse,
    ReviewListItem,
    ReviewDetail,
    ReviewCommentsResponse,
    ReviewCommentSchema,
    RetryResponse
)
from app.dependencies import get_current_user
from app.exceptions import HTTP404, HTTP400
from app.tasks.review_tasks import run_review_pipeline


router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=ReviewListResponse)
async def get_reviews(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status: str = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReviewListResponse:
    """
    Get paginated list of reviews for the authenticated user.
    """
    offset = (page - 1) * limit

    # Base query — join through pull_request and repository to filter by user
    base_query = (
        select(Review)
        .join(Review.pull_request)
        .join(PullRequest.repository)
        .where(Repository.owner_id == current_user.id)
        .options(
            selectinload(Review.pull_request)
        )
    )

    # Apply status filter if provided
    if status:
        base_query = base_query.where(Review.status == status)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    reviews_result = await db.execute(
        base_query
        .order_by(Review.triggered_at.desc())
        .offset(offset)
        .limit(limit)
    )
    reviews = reviews_result.scalars().all()

    return ReviewListResponse(
        items=[ReviewListItem.model_validate(r) for r in reviews],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{review_id}", response_model=ReviewDetail)
async def get_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReviewDetail:
    """
    Get full review detail including agent results and comments.
    """
    result = await db.execute(
        select(Review)
        .join(Review.pull_request)
        .join(PullRequest.repository)
        .where(
            Review.id == review_id,
            Repository.owner_id == current_user.id
        )
        .options(
            selectinload(Review.pull_request),
            selectinload(Review.agent_results),
            selectinload(Review.comments)
        )
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTP404("Review not found")

    return ReviewDetail.model_validate(review)


@router.get("/{review_id}/comments", response_model=ReviewCommentsResponse)
async def get_review_comments(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReviewCommentsResponse:
    """
    Get all comments for a specific review.
    """
    # Verify review belongs to current user
    review_result = await db.execute(
        select(Review)
        .join(Review.pull_request)
        .join(PullRequest.repository)
        .where(
            Review.id == review_id,
            Repository.owner_id == current_user.id
        )
    )
    review = review_result.scalar_one_or_none()

    if not review:
        raise HTTP404("Review not found")

    # Fetch comments
    comments_result = await db.execute(
        select(ReviewComment)
        .where(ReviewComment.review_id == review_id)
        .order_by(ReviewComment.created_at.asc())
    )
    comments = comments_result.scalars().all()

    return ReviewCommentsResponse(
        items=[ReviewCommentSchema.model_validate(c) for c in comments],
        total=len(comments)
    )


@router.post("/{review_id}/retry", response_model=RetryResponse, status_code=202)
async def retry_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RetryResponse:
    """
    Re-enqueue a failed review for reprocessing.
    Only works if review status is failed.
    """
    # Verify review belongs to current user
    result = await db.execute(
        select(Review)
        .join(Review.pull_request)
        .join(PullRequest.repository)
        .where(
            Review.id == review_id,
            Repository.owner_id == current_user.id
        )
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTP404("Review not found")

    if review.status != ReviewStatus.failed.value:
        raise HTTP400(
            f"Review cannot be retried — current status is {review.status}"
        )

    # Reset review status
    review.status = ReviewStatus.pending.value
    review.error_message = None
    await db.commit()

    # Re-enqueue task
    run_review_pipeline.delay(str(review_id))

    logger.info(f"Review {review_id} re-enqueued by user {current_user.username}")

    return RetryResponse(
        message="Review re-queued successfully",
        review_id=review_id
    )