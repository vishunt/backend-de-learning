from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from faker import Faker
import random
import os
from datetime import datetime

load_dotenv()

Base = declarative_base()
fake = Faker()

class RawSale(Base):
    __tablename__ = "raw_sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String)
    product = Column(String)
    category = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    sale_date = Column(DateTime)
    region = Column(String)
    ingested_at = Column(DateTime, default=datetime.utcnow)


def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Tables created.")


def seed_raw_data(n=200):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    db = Session()

    products = {
        "Electronics": ["Laptop", "Phone", "Tablet", "Monitor"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket", "Shoes"],
        "Food": ["Coffee", "Tea", "Chocolate", "Snacks"],
    }
    regions = ["North", "South", "East", "West"]

    records = []
    for _ in range(n):
        category = random.choice(list(products.keys()))
        product = random.choice(products[category])
        records.append(RawSale(
            customer_name=fake.name(),
            product=product,
            category=category,
            quantity=random.randint(1, 20),
            unit_price=round(random.uniform(5.0, 500.0), 2),
            sale_date=fake.date_time_between(start_date="-1y", end_date="now"),
            region=random.choice(regions),
        ))

    db.bulk_save_objects(records)
    db.commit()
    db.close()
    print(f"Seeded {n} raw sales records.")


if __name__ == "__main__":
    create_tables()
    seed_raw_data()