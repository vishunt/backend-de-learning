import pandera as pa
from pandera import Column, DataFrameSchema, Check
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))


# Define the schema for transformed data
transformed_schema = DataFrameSchema({
    "customer_name": Column(str, nullable=False),
    "product": Column(str, nullable=False),
    "category": Column(str, nullable=False),
    "quantity": Column(int, checks=[
        Check.greater_than(0, error="quantity must be positive")
    ]),
    "unit_price": Column(float, checks=[
        Check.greater_than(0.0, error="unit_price must be positive")
    ]),
    "total_amount": Column(float, checks=[
        Check.greater_than(0.0, error="total_amount must be positive")
    ]),
    "sale_month": Column(int, checks=[
        Check.in_range(1, 12, error="sale_month must be between 1 and 12")
    ]),
    "sale_year": Column(int, checks=[
        Check.greater_than(2000, error="sale_year must be after 2000")
    ]),
    "region": Column(str, checks=[
        Check.isin(["North", "South", "East", "West"],
                   error="region must be one of North, South, East, West")
    ]),
})


def validate_transformed_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM transformed_sales", con=engine)
    print(f"Validating {len(df)} records...")

    try:
        transformed_schema.validate(df, lazy=True)
        print("Validation passed. All records are clean.")
        return True
    except pa.errors.SchemaErrors as e:
        print(f"Validation FAILED. {len(e.failure_cases)} issues found:")
        print(e.failure_cases)
        return False


if __name__ == "__main__":
    validate_transformed_data()