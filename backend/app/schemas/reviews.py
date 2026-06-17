import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AgentResultSchema(BaseModel):
    id: uuid.UUID
    agent_type: str
    raw_output: dict
    issues_count: Optional[int] = None
    score: Optional[int] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCommentSchema(BaseModel):
    id: uuid.UUID
    body: str
    file: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None
    severity: Optional[str] = None
    agent_type: str
    posted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PullRequestSummary(BaseModel):
    id: uuid.UUID
    pr_number: int
    title: str
    author: str
    base_branch: str
    head_branch: str

    class Config:
        from_attributes = True


class ReviewListItem(BaseModel):
    id: uuid.UUID
    status: str
    overall_score: Optional[int] = None
    pull_request: PullRequestSummary
    triggered_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewDetail(BaseModel):
    id: uuid.UUID
    status: str
    overall_score: Optional[int] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    pull_request: PullRequestSummary
    agent_results: list[AgentResultSchema] = []
    comments: list[ReviewCommentSchema] = []
    triggered_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    items: list[ReviewListItem]
    total: int
    page: int
    limit: int


class ReviewCommentsResponse(BaseModel):
    items: list[ReviewCommentSchema]
    total: int


class RetryResponse(BaseModel):
    message: str
    review_id: uuid.UUID