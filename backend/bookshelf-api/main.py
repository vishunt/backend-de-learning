from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Book, Base
from schemas import BookCreate, BookResponse, BookUpdate
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookshelf API", version="0.3.0")

@app.get("/books", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()