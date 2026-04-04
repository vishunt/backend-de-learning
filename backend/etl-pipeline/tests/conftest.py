import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

@pytest.fixture(scope="session")
def db_engine():
    """Real database engine using etl_db."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def sample_raw_df():
    """A clean sample DataFrame simulating raw_sales data."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "customer_name": ["Alice Smith", "bob jones", "  Carol White  ", "Dave Brown", "Eve Davis"],
        "product": ["Laptop", "Phone", "T-Shirt", "Coffee", "Tablet"],
        "category": ["Electronics", "Electronics", "Clothing", "Food", "Electronics"],
        "quantity": [2, 0, 3, 5, 1],        # row 2 has quantity=0 (bad data)
        "unit_price": [999.99, 299.99, 29.99, 9.99, 499.99],
        "sale_date": pd.to_datetime([
            "2024-01-15", "2024-03-20", "2024-06-10",
            "2024-09-05", "2024-11-30"
        ]),
        "region": ["north", "South", "east", "West", "north"],
        "ingested_at": pd.to_datetime(["2024-01-15"] * 5),
    })


@pytest.fixture(scope="function")
def bad_df():
    """DataFrame with multiple data quality issues for validation tests."""
    return pd.DataFrame({
        "customer_name": ["Alice", None],
        "product": ["Laptop", "Phone"],
        "category": ["Electronics", "Electronics"],
        "quantity": [-1, 2],               # negative quantity
        "unit_price": [999.99, -50.0],     # negative price
        "total_amount": [-999.99, -100.0], # negative total
        "sale_month": [13, 3],             # month 13 is invalid
        "sale_year": [2024, 2024],
        "region": ["North", "InvalidRegion"],  # invalid region
        "sale_date": pd.to_datetime(["2024-01-15", "2024-03-20"]),
        "ingested_at": pd.to_datetime(["2024-01-15", "2024-03-20"]),
        "transformed_at": pd.to_datetime(["2024-01-15", "2024-03-20"]),
    })