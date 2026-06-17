import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.enums import ReviewStatus


class Review(Base):
    __tablename__ = "reviews"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to PullRequest
    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Review state
    status: Mapped[ReviewStatus] = mapped_column(
        String(20),
        default=ReviewStatus.pending.value,
        nullable=False,
        index=True
    )
    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    # Error tracking
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship(
        "PullRequest",
        back_populates="reviews"
    )
    agent_results: Mapped[list["AgentResult"]] = relationship(
        "AgentResult",
        back_populates="review",
        cascade="all, delete-orphan"
    )
    comments: Mapped[list["ReviewComment"]] = relationship(
        "ReviewComment",
        back_populates="review",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Review {self.id} status={self.status}>"