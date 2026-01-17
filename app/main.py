from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware

# Setup logging early
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{__version__}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Configured channels: {len(settings.CITY_CHANNELS)}")

    yield

    # Shutdown
    logger.info("Shutting down application")


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        description="""
## Baity Telegram Bot API

A webhook service for posting real estate listings to city-specific Telegram channels.

### Features
- Receive real estate webhooks from Baity backend
- Post listings to configured Telegram channels
- Support for photos and formatted messages
- Batch and async processing options

### Authentication
All webhook endpoints require an `X-Api-Key` header.
        """,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add middleware
    app.add_middleware(LoggingMiddleware)

    # CORS middleware (configure as needed)
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Legacy endpoint support (for backward compatibility)
    # Remove these after migrating to v1 endpoints
    from app.api.v1.endpoints import webhook, health

    app.include_router(
        webhook.router,
        prefix="/webhook",
        tags=["Legacy"],
        deprecated=True,
    )

    @app.get("/health", tags=["Legacy"], deprecated=True)
    async def legacy_health() -> dict[str, str]:
        """Legacy health endpoint. Use /api/v1/health instead."""
        return {"status": "ok"}

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
