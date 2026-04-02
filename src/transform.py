import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))


def extract_raw_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM raw_sales", con=engine)
    print(f"Extracted {len(df)} raw records.")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Drop rows with any nulls in critical columns
    df = df.dropna(subset=["customer_name", "product", "quantity", "unit_price", "sale_date"])

    # Remove duplicates
    df = df.drop_duplicates()

    # Ensure correct types
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    df["sale_date"] = pd.to_datetime(df["sale_date"])

    # Derive new columns
    df["total_amount"] = df["quantity"] * df["unit_price"]
    df["sale_month"] = df["sale_date"].dt.month
    df["sale_year"] = df["sale_date"].dt.year
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df["region"] = df["region"].str.strip().str.title()
    df["category"] = df["category"].str.strip().str.title()

    # Remove bad data
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]

    df["transformed_at"] = datetime.utcnow()

    print(f"Transformed {len(df)} records.")
    return df


def load_transformed(df: pd.DataFrame):
    engine = get_engine()
    df.to_sql(
        "transformed_sales",
        con=engine,
        if_exists="replace",
        index=False
    )
    print(f"Loaded {len(df)} records into transformed_sales.")


if __name__ == "__main__":
    raw = extract_raw_data()
    transformed = transform(raw)
    load_transformed(transformed)