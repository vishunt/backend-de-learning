from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.book import Book
from models.user import User
from schemas.book import BookCreate, BookResponse, BookUpdate
from routers.auth import get_current_user
from typing import List
from typing import List, Optional
import json
from redis_client import redis_client


router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=List[BookResponse])
def get_books(
    skip: int = 0,
    limit: int = 10,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    published: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Build cache key from all params
    cache_key = f"books:{skip}:{limit}:{author}:{genre}:{published}"
    
    # Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # If not in cache, query DB
    query = db.query(Book)
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    if published is not None:
        query = query.filter(Book.published == published)
    
    books = query.offset(skip).limit(limit).all()
    
    # Convert to dict for JSON serialization
    books_data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "year": b.year,
            "genre": b.genre,
            "published": b.published,
            "created_at": b.created_at.isoformat()
        }
        for b in books
    ]
    
    # Store in cache for 60 seconds
    redis_client.setex(cache_key, 60, json.dumps(books_data))
    
    return books_data

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    updates: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()