from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time

from app.config import settings
from app.database import engine, Base
from app.routers import auth, webhook, reviews, repositories


# ─────────────────────────────────────────
# Lifespan — startup and shutdown events
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()


# ─────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Code Review Platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ─────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Request logging middleware
# ─────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(
        f"Request: {request.method} {request.url.path}"
    )

    response = await call_next(request)

    process_time = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={process_time}ms"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# ─────────────────────────────────────────
# Global exception handler
# ─────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} "
        f"{request.url.path}: {str(exc)}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url.path)
        }
    )


# ─────────────────────────────────────────
# Register routers
# ─────────────────────────────────────────
app.include_router(auth.router)
app.include_router(webhook.router)
app.include_router(reviews.router)
app.include_router(repositories.router)


# ─────────────────────────────────────────
# Health check endpoint
# ─────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Railway pings this to confirm container is alive.
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "app": settings.APP_NAME,
    }


# ─────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────
@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }