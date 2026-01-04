"""API middleware for logging and error handling."""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("pii_shield")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Log request
        logger.info(f"{request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response time
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} ({elapsed_ms:.2f}ms)"
        )

        # Add timing header
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

        return response
