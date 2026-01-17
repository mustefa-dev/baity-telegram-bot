import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Log request
        start_time = time.perf_counter()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Started"
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Error after {process_time:.2f}ms: {e}"
            )
            raise

        # Calculate processing time
        process_time = (time.perf_counter() - start_time) * 1000

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"{response.status_code} ({process_time:.2f}ms)"
        )

        return response
