import enum


class ReviewStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PRStatus(enum.Enum):
    open = "open"
    closed = "closed"
    merged = "merged"


class AgentType(enum.Enum):
    code_review = "code_review"
    security = "security"


class Severity(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"