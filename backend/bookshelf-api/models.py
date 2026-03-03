from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())