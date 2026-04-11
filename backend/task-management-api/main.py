from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import engine
from models import User, Task
from database import Base
from routers import auth, tasks
from middleware.rate_limit import RateLimitMiddleware
from middleware.logging_middleware import LoggingMiddleware
from logger import get_logger
import traceback
import time
import sqlalchemy

logger = get_logger("main")

# Wait for Postgres to be ready before creating tables
def wait_for_db(retries=10, delay=3):
    for attempt in range(retries):
        try:
            with engine.connect() as conn:
                logger.info("Database is ready!")
                return
        except sqlalchemy.exc.OperationalError:
            logger.warning(f"Database not ready, retrying in {delay}s... (attempt {attempt + 1}/{retries})")
            time.sleep(delay)
    raise Exception("Database never became ready after multiple retries")

wait_for_db()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API", version="1.0.0")
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
app.add_middleware(LoggingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Task Management API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}