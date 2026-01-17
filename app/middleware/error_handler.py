from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import (
    AuthenticationError,
    BaityBotException,
    ChannelNotFoundError,
    ConfigurationError,
    TelegramError,
    TelegramRateLimitError,
)
from app.core.logging import get_logger
from app.schemas.response import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers for the application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors."""
        request_id = getattr(request.state, "request_id", None)
        details = [
            ErrorDetail(
                field=".".join(str(loc) for loc in error["loc"]),
                message=error["msg"],
                code=error["type"],
            )
            for error in exc.errors()
        ]

        response = ErrorResponse(
            error="validation_error",
            message="Request validation failed",
            details=details,
            request_id=request_id,
        )

        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        """Handle authentication errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="authentication_error",
            message=exc.message,
            request_id=request_id,
        )

        logger.warning(f"Authentication error: {exc.message}")
        return JSONResponse(
            status_code=401,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(ChannelNotFoundError)
    async def channel_not_found_exception_handler(
        request: Request,
        exc: ChannelNotFoundError,
    ) -> JSONResponse:
        """Handle channel not found errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="channel_not_found",
            message=exc.message,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=404,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(TelegramRateLimitError)
    async def telegram_rate_limit_exception_handler(
        request: Request,
        exc: TelegramRateLimitError,
    ) -> JSONResponse:
        """Handle Telegram rate limit errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="rate_limited",
            message=exc.message,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=429,
            content=response.model_dump(mode="json"),
            headers={"Retry-After": str(exc.retry_after)},
        )

    @app.exception_handler(TelegramError)
    async def telegram_exception_handler(
        request: Request,
        exc: TelegramError,
    ) -> JSONResponse:
        """Handle Telegram errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="telegram_error",
            message=exc.message,
            request_id=request_id,
        )

        logger.error(f"Telegram error: {exc.message}")
        return JSONResponse(
            status_code=502,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(ConfigurationError)
    async def configuration_exception_handler(
        request: Request,
        exc: ConfigurationError,
    ) -> JSONResponse:
        """Handle configuration errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="configuration_error",
            message=exc.message,
            request_id=request_id,
        )

        logger.error(f"Configuration error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(BaityBotException)
    async def baity_bot_exception_handler(
        request: Request,
        exc: BaityBotException,
    ) -> JSONResponse:
        """Handle general application errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="application_error",
            message=exc.message,
            request_id=request_id,
        )

        logger.error(f"Application error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected errors."""
        request_id = getattr(request.state, "request_id", None)
        response = ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred",
            request_id=request_id,
        )

        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content=response.model_dump(mode="json"),
        )
