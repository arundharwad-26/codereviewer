import uuid
from datetime import datetime
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.review import Review
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.agent_result import AgentResult
from app.models.review_comment import ReviewComment
from app.models.enums import ReviewStatus, AgentType
from app.services import github_service, ai_service
from app.agents.merger import merge_results
from app.exceptions import (
    GitHubAPIError,
    AIServiceError,
    ReviewNotFoundError
)


async def mark_failed(
    review_id: uuid.UUID,
    session: AsyncSession,
    error_message: str
) -> None:
    """
    Mark a review as failed and log the error.
    """
    try:
        review = await session.get(Review, review_id)
        if review:
            review.status = ReviewStatus.failed.value
            review.error_message = error_message
            review.updated_at = datetime.utcnow()
            await session.commit()
            logger.error(f"Review {review_id} marked as failed: {error_message}")
    except Exception as e:
        logger.error(f"Failed to mark review as failed: {str(e)}")


async def run_pipeline(
    review_id: uuid.UUID,
    session: AsyncSession
) -> None:
    """
    Main orchestrator pipeline — 8 steps in order.
    Called by the Celery task.
    """
    logger.info(f"Starting pipeline for review {review_id}")

    # ─────────────────────────────────────────
    # Step 1 — Load from DB
    # ─────────────────────────────────────────
    try:
        result = await session.execute(
            select(Review)
            .options(
                selectinload(Review.pull_request)
                .selectinload(PullRequest.repository)
            )
            .where(Review.id == review_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            raise ReviewNotFoundError(f"Review {review_id} not found")

        pull_request = review.pull_request
        repository = pull_request.repository
        repo_full_name = repository.full_name
        pr_number = pull_request.pr_number

        logger.info(
            f"Loaded review for PR #{pr_number} "
            f"in {repo_full_name}"
        )

    except ReviewNotFoundError as e:
        logger.error(str(e))
        return

    # ─────────────────────────────────────────
    # Step 2 — Update status to processing
    # ─────────────────────────────────────────
    try:
        review.status = ReviewStatus.processing.value
        review.started_at = datetime.utcnow()
        await session.commit()
        logger.info(f"Review {review_id} status set to processing")

    except Exception as e:
        await mark_failed(review_id, session, str(e))
        return

    # ─────────────────────────────────────────
    # Step 3 — Fetch diff
    # ─────────────────────────────────────────
    try:
        diff = await github_service.get_pr_diff(repo_full_name, pr_number)
        logger.info(f"Fetched diff for PR #{pr_number}")

    except GitHubAPIError as e:
        await mark_failed(review_id, session, str(e))
        return

    # ─────────────────────────────────────────
    # Step 4 — Run Code Review Agent
    # ─────────────────────────────────────────
    try:
        code_review_output = await ai_service.run_code_review_agent(diff)

        # Save AgentResult immediately after
        meta = code_review_output.pop("_meta", {})
        code_agent_result = AgentResult(
            review_id=review_id,
            agent_type=AgentType.code_review.value,
            raw_output=code_review_output,
            issues_count=len(code_review_output.get("issues", [])),
            score=code_review_output.get("overall_score"),
            tokens_used=meta.get("tokens_used"),
            processing_time_ms=meta.get("processing_time_ms")
        )
        session.add(code_agent_result)
        await session.commit()
        logger.info(f"Code review agent result saved for review {review_id}")

    except AIServiceError as e:
        await mark_failed(review_id, session, str(e))
        return

    # ─────────────────────────────────────────
    # Step 5 — Run Security Agent
    # ─────────────────────────────────────────
    try:
        security_output = await ai_service.run_security_agent(
            diff,
            code_review_output
        )

        # Save AgentResult immediately after
        meta = security_output.pop("_meta", {})
        security_agent_result = AgentResult(
            review_id=review_id,
            agent_type=AgentType.security.value,
            raw_output=security_output,
            issues_count=len(security_output.get("vulnerabilities", [])),
            tokens_used=meta.get("tokens_used"),
            processing_time_ms=meta.get("processing_time_ms")
        )
        session.add(security_agent_result)
        await session.commit()
        logger.info(f"Security agent result saved for review {review_id}")

    except AIServiceError as e:
        # Keep code review result — only security failed
        error_msg = f"Security agent failed: {str(e)}"
        await mark_failed(review_id, session, error_msg)
        return

    # ─────────────────────────────────────────
    # Step 6 — Merge results
    # ─────────────────────────────────────────
    report = merge_results(code_review_output, security_output)
    logger.info(f"Results merged for review {review_id}")

    # ─────────────────────────────────────────
    # Step 7 — Write to DB
    # ─────────────────────────────────────────
    try:
        # Update review row
        review.status = ReviewStatus.completed.value
        review.overall_score = report["overall_score"]
        review.summary = report["code_review"]["summary"]
        review.completed_at = datetime.utcnow()

        # Insert code review comments
        for issue in report["code_review"]["issues"]:
            comment = ReviewComment(
                review_id=review_id,
                body=issue.get("message", ""),
                file=issue.get("file"),
                line=issue.get("line"),
                suggestion=issue.get("suggestion"),
                severity=issue.get("severity"),
                agent_type=AgentType.code_review.value,
                posted=False
            )
            session.add(comment)

        # Insert security comments
        for vuln in report["security"]["vulnerabilities"]:
            comment = ReviewComment(
                review_id=review_id,
                body=vuln.get("description", ""),
                file=vuln.get("file"),
                line=vuln.get("line"),
                suggestion=vuln.get("recommendation"),
                severity=report["security"]["severity"],
                agent_type=AgentType.security.value,
                posted=False
            )
            session.add(comment)

        await session.commit()
        logger.info(f"Review {review_id} written to DB with all comments")

    except Exception as e:
        await mark_failed(review_id, session, str(e))
        return

    # ─────────────────────────────────────────
    # Step 8 — Post to GitHub
    # ─────────────────────────────────────────
    try:
        # Fetch unposted comments
        comments_result = await session.execute(
            select(ReviewComment)
            .where(
                ReviewComment.review_id == review_id,
                ReviewComment.posted == False
            )
        )
        comments = comments_result.scalars().all()

        # Post each comment individually
        for comment in comments:
            try:
                await github_service.post_review_comment(
                    repo_full_name,
                    pr_number,
                    comment.body
                )
                comment.posted = True
                await session.commit()

            except GitHubAPIError as e:
                # Log but do not fail entire review
                logger.error(
                    f"Failed to post comment {comment.id}: {str(e)}"
                )

        # Post final summary
        await github_service.create_review_summary(
            repo_full_name,
            pr_number,
            report
        )

        logger.info(
            f"Pipeline complete for review {review_id} — "
            f"PR #{pr_number} in {repo_full_name}"
        )

    except Exception as e:
        # GitHub posting failed but analysis is complete
        # Do not mark as failed — data is already saved
        logger.error(
            f"GitHub posting failed for review {review_id}: {str(e)}"
        )