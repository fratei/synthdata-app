"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return service health status."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
