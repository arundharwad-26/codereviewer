import uuid
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.repository import Repository
from app.models.review import Review
from app.models.pull_request import PullRequest
from app.models.enums import ReviewStatus
from app.schemas.repositories import (
    RepositoryResponse,
    RepositoryListResponse,
    ConnectRepositoryRequest,
    RepositoryStatsResponse,
    ReviewsByStatus,
    RecentReviewSummary
)
from app.dependencies import get_current_user
from app.exceptions import HTTP404, HTTP400


router = APIRouter(prefix="/api/repos", tags=["repositories"])


async def verify_github_repo_access(
    full_name: str,
    github_token: str
) -> dict:
    """
    Verify user has access to the repository on GitHub.
    Returns repo data from GitHub API.
    Raises HTTP400 if repo not found or no access.
    """
    url = f"https://api.github.com/repos/{full_name}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30.0
        )

        if response.status_code == 404:
            raise HTTP400(
                f"Repository {full_name} not found or you don't have access"
            )

        if response.status_code != 200:
            raise HTTP400(
                f"Failed to verify repository access: {response.text}"
            )

        return response.json()


@router.get("", response_model=RepositoryListResponse)
async def get_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RepositoryListResponse:
    """
    Get all repositories connected by the authenticated user.
    """
    result = await db.execute(
        select(Repository)
        .where(
            Repository.owner_id == current_user.id,
            Repository.is_active == True
        )
        .order_by(Repository.created_at.desc())
    )
    repositories = result.scalars().all()

    return RepositoryListResponse(
        items=[RepositoryResponse.model_validate(r) for r in repositories],
        total=len(repositories)
    )


@router.post("", response_model=RepositoryResponse, status_code=201)
async def connect_repository(
    request: ConnectRepositoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RepositoryResponse:
    """
    Connect a new GitHub repository.
    Verifies access on GitHub before saving.
    """
    full_name = request.full_name.strip()

    # Validate format owner/repo
    if "/" not in full_name or len(full_name.split("/")) != 2:
        raise HTTP400(
            "Invalid repository format. Use owner/repo-name"
        )

    # Check if already connected
    existing_result = await db.execute(
        select(Repository).where(
            Repository.full_name == full_name,
            Repository.owner_id == current_user.id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        if existing.is_active:
            raise HTTP400(
                f"Repository {full_name} is already connected"
            )
        else:
            # Reactivate if previously disconnected
            existing.is_active = True
            await db.commit()
            await db.refresh(existing)
            logger.info(
                f"Reactivated repository {full_name} "
                f"for user {current_user.username}"
            )
            return RepositoryResponse.model_validate(existing)

    # Verify access on GitHub
    github_data = await verify_github_repo_access(
        full_name,
        current_user.github_access_token
    )

    # Create repository row
    repository = Repository(
        owner_id=current_user.id,
        full_name=full_name,
        name=github_data.get("name", full_name.split("/")[1]),
        language=github_data.get("language"),
        is_private=github_data.get("private", False),
        is_active=True
    )
    db.add(repository)
    await db.commit()
    await db.refresh(repository)

    logger.info(
        f"Connected repository {full_name} "
        f"for user {current_user.username}"
    )

    return RepositoryResponse.model_validate(repository)


@router.get("/{repo_id}/stats", response_model=RepositoryStatsResponse)
async def get_repository_stats(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RepositoryStatsResponse:
    """
    Get analytics and stats for a specific repository.
    """
    # Verify repo belongs to current user
    repo_result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.owner_id == current_user.id
        )
    )
    repository = repo_result.scalar_one_or_none()

    if not repository:
        raise HTTP404("Repository not found")

    # Get total reviews count
    total_result = await db.execute(
        select(func.count(Review.id))
        .join(Review.pull_request)
        .where(PullRequest.repository_id == repo_id)
    )
    total_reviews = total_result.scalar() or 0

    # Get average score
    avg_result = await db.execute(
        select(func.avg(Review.overall_score))
        .join(Review.pull_request)
        .where(
            PullRequest.repository_id == repo_id,
            Review.overall_score.isnot(None)
        )
    )
    average_score = avg_result.scalar()
    if average_score:
        average_score = round(float(average_score), 2)

    # Get reviews by status
    status_result = await db.execute(
        select(Review.status, func.count(Review.id))
        .join(Review.pull_request)
        .where(PullRequest.repository_id == repo_id)
        .group_by(Review.status)
    )
    status_rows = status_result.all()

    reviews_by_status = ReviewsByStatus()
    for status, count in status_rows:
        if hasattr(reviews_by_status, status):
            setattr(reviews_by_status, status, count)

    # Get recent reviews
    recent_result = await db.execute(
        select(Review)
        .join(Review.pull_request)
        .where(PullRequest.repository_id == repo_id)
        .order_by(Review.triggered_at.desc())
        .limit(5)
    )
    recent_reviews = recent_result.scalars().all()

    return RepositoryStatsResponse(
        repo=RepositoryResponse.model_validate(repository),
        total_reviews=total_reviews,
        average_score=average_score,
        reviews_by_status=reviews_by_status,
        recent_reviews=[
            RecentReviewSummary.model_validate(r)
            for r in recent_reviews
        ]
    )