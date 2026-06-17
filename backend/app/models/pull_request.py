import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.enums import PRStatus


class PullRequest(Base):
    __tablename__ = "pull_requests"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to Repository
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # PR info from GitHub
    pr_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    base_branch: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    head_branch: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    diff_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    # Status
    status: Mapped[PRStatus] = mapped_column(
        String(20),
        default=PRStatus.open.value,
        nullable=False
    )

    # Timestamps
    pr_created_at: Mapped[datetime] = mapped_column(
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
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="pull_requests"
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="pull_request",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PullRequest #{self.pr_number} {self.title}>"