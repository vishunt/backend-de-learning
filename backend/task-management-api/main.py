from fastapi import FastAPI
from database import engine
from models import User, Task
from database import Base
from routers import auth, tasks
from middleware.rate_limit import RateLimitMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API", version="1.0.0")

app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Task Management API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}