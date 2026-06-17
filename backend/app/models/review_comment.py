import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.enums import Severity


class ReviewComment(Base):
    __tablename__ = "review_comments"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to Review
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Comment content
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    file: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    line: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    suggestion: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    # Severity
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )

    # Source agent
    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # GitHub posting status
    posted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    github_comment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    # Timestamps
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
    review: Mapped["Review"] = relationship(
        "Review",
        back_populates="comments"
    )

    def __repr__(self) -> str:
        return f"<ReviewComment {self.id} posted={self.posted}>"