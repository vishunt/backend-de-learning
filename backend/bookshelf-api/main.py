from fastapi import FastAPI, HTTPException
from schemas import BookCreate, BookResponse, BookUpdate
from datetime import datetime
from typing import List

app = FastAPI(title="Bookshelf API", version="0.2.0")

books_db = {}
counter = 1

@app.get("/")
def root():
    return {"message": "Bookshelf API", "version": "0.2.0"}

@app.get("/books", response_model=List[BookResponse])
def get_books():
    return list(books_db.values())

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]

@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    global counter
    new_book = {**book.dict(), "id": counter, "created_at": datetime.now()}
    books_db[counter] = new_book
    counter += 1
    return new_book

@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in updates.dict(exclude_unset=True).items():
        books_db[book_id][field] = value
    return books_db[book_id]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[book_id]