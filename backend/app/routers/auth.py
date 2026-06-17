import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.auth import TokenResponse, UserProfileResponse
from app.dependencies import create_access_token, get_current_user
from app.exceptions import HTTP401


router = APIRouter(prefix="/api/auth", tags=["auth"])

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


@router.get("/github")
async def github_login() -> RedirectResponse:
    params = (
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=repo,user:email"
        f"&allow_signup=true"
    )
    return RedirectResponse(url=f"{GITHUB_AUTH_URL}{params}")


@router.get("/callback")
async def github_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    # Step 1 — Exchange code for GitHub access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            timeout=30.0
        )

        if token_response.status_code != 200:
            logger.error(f"GitHub token exchange failed: {token_response.text}")
            raise HTTP401("Failed to exchange GitHub code for token")

        token_data = token_response.json()
        github_access_token = token_data.get("access_token")

        if not github_access_token:
            raise HTTP401("No access token in GitHub response")

    # Step 2 — Fetch GitHub user profile
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30.0
        )

        if user_response.status_code != 200:
            logger.error(f"GitHub user fetch failed: {user_response.text}")
            raise HTTP401("Failed to fetch GitHub user profile")

        github_user = user_response.json()

    # Step 3 — Create or update user in DB
    github_id = str(github_user["id"])

    result = await db.execute(
        select(User).where(User.github_id == github_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.username = github_user["login"]
        user.avatar_url = github_user.get("avatar_url")
        user.email = github_user.get("email")
        user.github_access_token = github_access_token
        logger.info(f"Updated existing user: {user.username}")
    else:
        user = User(
            github_id=github_id,
            username=github_user["login"],
            avatar_url=github_user.get("avatar_url"),
            email=github_user.get("email"),
            github_access_token=github_access_token,
        )
        db.add(user)
        logger.info(f"Created new user: {github_user['login']}")

    await db.commit()
    await db.refresh(user)

    # Step 4 — Generate JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
        }
    )

    logger.info(f"JWT generated for user: {user.username}")

    # Step 5 — Redirect to frontend with token
    redirect_url = (
        f"http://localhost:5173/auth/callback"
        f"?token={access_token}"
        f"&username={user.username}"
        f"&avatar_url={user.avatar_url or ''}"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserProfileResponse:
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
    )