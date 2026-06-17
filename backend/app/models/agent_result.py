import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
from app.models.enums import AgentType


class AgentResult(Base):
    __tablename__ = "agent_results"

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

    # Agent info
    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # Raw output from AI agent
    raw_output: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Extracted metrics
    issues_count: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    # Processing info
    tokens_used: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    processing_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    review: Mapped["Review"] = relationship(
        "Review",
        back_populates="agent_results"
    )

    def __repr__(self) -> str:
        return f"<AgentResult {self.agent_type} review={self.review_id}>"