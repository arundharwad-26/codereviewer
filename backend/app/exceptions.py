from fastapi import HTTPException, status


# Base custom exception
class AppBaseException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# GitHub service exceptions
class GitHubAPIError(AppBaseException):
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class GitHubWebhookValidationError(AppBaseException):
    pass


# AI service exceptions
class AIServiceError(AppBaseException):
    def __init__(self, message: str, agent_type: str = None):
        self.agent_type = agent_type
        super().__init__(message)


class AIResponseParseError(AppBaseException):
    pass


# Database exceptions
class ReviewNotFoundError(AppBaseException):
    pass


class RepositoryNotFoundError(AppBaseException):
    pass


class UserNotFoundError(AppBaseException):
    pass


# Auth exceptions
class InvalidTokenError(AppBaseException):
    pass


class TokenExpiredError(AppBaseException):
    pass


# HTTP exceptions - used directly in routers
class HTTP401(HTTPException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class HTTP403(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class HTTP404(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class HTTP400(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )