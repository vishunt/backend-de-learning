from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis_client import redis_client

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        try:
            current = redis_client.incr(key)
            if current == 1:
                redis_client.expire(key, self.window_seconds)

            if current > self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Too many requests. Max {self.max_requests} per {self.window_seconds} seconds."
                    }
                )
        except Exception:
            # If Redis is down, don't block requests
            pass

        return await call_next(request)