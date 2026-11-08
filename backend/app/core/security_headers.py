"""Defensive HTTP Security Headers & In-Memory Rate Limiting Middleware.

Zero-cost, lightweight, in-memory implementation for production resilience.
"""

import time
import os
from typing import Dict, List, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class InMemoryRateLimiter:
    """Sliding-window rate limiter per client IP."""

    DEFAULT_LIMITS: Dict[str, Tuple[int, float]] = {
        "/chat": (30, 60.0),
        "/contact": (6, 60.0),
        "/api/cv-request": (6, 60.0),
    }

    def __init__(self, limits: Dict[str, Tuple[int, float]] = None):
        self.limits = limits or self.DEFAULT_LIMITS
        self._history: Dict[Tuple[str, str], List[float]] = {}

    def reset(self) -> None:
        """Clear history (used in test fixtures)."""
        self._history.clear()

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP respecting X-Forwarded-For if available."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def is_allowed(self, client_ip: str, path: str) -> Tuple[bool, int]:
        """Check if request is allowed under rate limits.

        Returns (allowed, retry_after_seconds).
        """
        # Allow disabling via environment variable if needed
        if os.environ.get("DISABLE_RATE_LIMIT") == "1":
            return True, 0

        now = time.time()
        for prefix, (max_reqs, window_sec) in self.limits.items():
            if path == prefix or path.startswith(prefix + "/"):
                key = (client_ip, prefix)
                timestamps = self._history.get(key, [])
                # Prune older requests outside the window
                cutoff = now - window_sec
                timestamps = [t for t in timestamps if t > cutoff]

                if len(timestamps) >= max_reqs:
                    oldest = timestamps[0]
                    retry_after = max(1, int(window_sec - (now - oldest)))
                    self._history[key] = timestamps
                    return False, retry_after

                timestamps.append(now)
                self._history[key] = timestamps
                return True, 0

        return True, 0


rate_limiter = InMemoryRateLimiter()


class SecurityHardeningMiddleware(BaseHTTPMiddleware):
    """Injects defensive HTTP security headers and enforces rate limits."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Rate Limiting check
        client_ip = rate_limiter.get_client_ip(request)
        path = request.url.path

        allowed, retry_after = rate_limiter.is_allowed(client_ip, path)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please wait before making more requests."
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                },
            )

        # 2. Process request
        response: Response = await call_next(request)

        # 3. Defensive Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        return response
