import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from logger import get_logger

logger = get_logger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration}ms"
        )
        
        return response