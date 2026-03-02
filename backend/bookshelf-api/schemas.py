from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookCreate(BaseModel):
    title: str = Field(...,min_length=1, max_length=255)
    author: str = Field(...,min_length=1, max_length=255)
    year: int = Field(..., ge=1000, le=2000)
    genre :Optional[str] = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    genre: Optional[str]
    created_at: datetime

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None