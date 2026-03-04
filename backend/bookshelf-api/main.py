from fastapi import FastAPI
from database import engine
from models import Base
from routers import books

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookshelf API", version="0.4.0")

app.include_router(books.router)

@app.get("/")
def root():
    return {"message": "Bookshelf API", "version": "0.4.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}