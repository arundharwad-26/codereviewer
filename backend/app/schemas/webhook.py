from pydantic import BaseModel
from typing import Optional


class GitHubUser(BaseModel):
    login: str
    id: int
    avatar_url: Optional[str] = None


class GitHubRepository(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    language: Optional[str] = None


class GitHubPullRequest(BaseModel):
    number: int
    title: str
    body: Optional[str] = None
    state: str
    created_at: str
    updated_at: str
    diff_url: Optional[str] = None
    user: GitHubUser
    head: dict
    base: dict


class GitHubWebhookPayload(BaseModel):
    action: str
    number: Optional[int] = None
    pull_request: Optional[GitHubPullRequest] = None
    repository: Optional[GitHubRepository] = None
    sender: Optional[GitHubUser] = None

    class Config:
        extra = "allow"


class WebhookResponse(BaseModel):
    message: str
    review_id: Optional[str] = None