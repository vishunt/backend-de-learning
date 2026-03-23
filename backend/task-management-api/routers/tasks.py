from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.user import User
from schemas.task import TaskCreate, TaskResponse, TaskUpdate
from routers.auth import get_current_user
from typing import List, Optional
from sqlalchemy import func
import json
from redis_client import redis_client

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"tasks:{current_user.id}:{skip}:{limit}:{completed}:{priority}"
    
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()
    
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "completed": t.completed,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "owner_id": t.owner_id,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        for t in tasks
    ]
    
    redis_client.setex(cache_key, 60, json.dumps(tasks_data))
    
    return tasks_data
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()

@router.get("/stats/summary")
def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(Task).filter(Task.owner_id == current_user.id).count()
    completed = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.completed == True
    ).count()
    pending = total - completed
    
    by_priority = {}
    for priority in ["low", "medium", "high", "critical"]:
        count = db.query(Task).filter(
            Task.owner_id == current_user.id,
            Task.priority == priority
        ).count()
        by_priority[priority] = count
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "by_priority": by_priority
    }    