import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class RepositoryBase(BaseModel):
    full_name: str
    name: str
    language: Optional[str] = None
    is_private: bool = False


class RepositoryResponse(RepositoryBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RepositoryListResponse(BaseModel):
    items: list[RepositoryResponse]
    total: int


class ConnectRepositoryRequest(BaseModel):
    full_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "owner/repo-name"
            }
        }


class RecentReviewSummary(BaseModel):
    id: uuid.UUID
    pr_number: int
    overall_score: Optional[int] = None
    status: str
    triggered_at: datetime

    class Config:
        from_attributes = True


class ReviewsByStatus(BaseModel):
    completed: int = 0
    failed: int = 0
    pending: int = 0
    processing: int = 0


class RepositoryStatsResponse(BaseModel):
    repo: RepositoryResponse
    total_reviews: int
    average_score: Optional[float] = None
    reviews_by_status: ReviewsByStatus
    recent_reviews: list[RecentReviewSummary] = []

    class Config:
        from_attributes = True