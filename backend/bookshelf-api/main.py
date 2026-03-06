from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
from fastapi import FastAPI
from database import engine
from models.book import Book
from models.user import User
from database import Base
from routers import books, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookshelf API", version="0.5.0")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.include_router(auth.router)
app.include_router(books.router)

@app.get("/")
def root():
    return {"message": "Bookshelf API", "version": "0.5.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}