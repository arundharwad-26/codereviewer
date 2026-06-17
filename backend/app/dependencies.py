import uuid
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData
from app.exceptions import HTTP401


# Bearer token scheme
security = HTTPBearer()


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    Called by auth router after successful OAuth.
    """
    from datetime import datetime, timedelta
    import copy

    payload = copy.deepcopy(data)
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT access token.
    Raises HTTP401 if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        username: str = payload.get("username")

        if user_id is None:
            raise HTTP401("Token missing subject")

        return TokenData(user_id=user_id, username=username)

    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}")
        raise HTTP401("Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency — decodes JWT and returns the current user.
    Inject into any protected route with:
    current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    token_data = decode_access_token(token)

    try:
        result = await db.execute(
            select(User).where(
                User.id == uuid.UUID(token_data.user_id)
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTP401("User not found")

        if not user.is_active:
            raise HTTP401("User account is inactive")

        return user

    except HTTP401:
        raise
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        raise HTTP401("Could not validate credentials")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Additional dependency — confirms user is active.
    Use this instead of get_current_user for extra safety.
    """
    if not current_user.is_active:
        raise HTTP401("Inactive user")
    return current_user