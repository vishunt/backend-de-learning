from fastapi import FastAPI
from database import engine
from models import User, Task
from database import Base
from routers import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Task Management API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}