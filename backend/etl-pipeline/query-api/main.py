from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from database import get_db
from models import SalesSummary, StagedSale

app = FastAPI(
    title="ETL Analytics Query API",
    description="Query layer on top of dbt analytics models",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "ETL Analytics Query API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/sales/summary", response_model=List[SalesSummary])
def get_sales_summary(
    category: Optional[str] = None,
    region: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated sales summary from dbt's sales_summary table.
    Filter by category, region, year, or month.
    """
    query = "SELECT * FROM dbt_analytics.sales_summary WHERE 1=1"
    params = {}

    if category:
        query += " AND category = :category"
        params["category"] = category
    if region:
        query += " AND region = :region"
        params["region"] = region
    if year:
        query += " AND sale_year = :year"
        params["year"] = year
    if month:
        query += " AND sale_month = :month"
        params["month"] = month

    query += " ORDER BY total_revenue DESC"

    result = db.execute(text(query), params)
    return [dict(row) for row in result]


@app.get("/sales/by-category")
def get_sales_by_category(db: Session = Depends(get_db)):
    """Total revenue grouped by category."""
    query = text("""
        SELECT
            category,
            SUM(total_revenue) as total_revenue,
            SUM(total_orders) as total_orders,
            SUM(total_units_sold) as total_units_sold
        FROM dbt_analytics.sales_summary
        GROUP BY category
        ORDER BY total_revenue DESC
    """)
    result = db.execute(query)
    return [dict(row) for row in result]


@app.get("/sales/by-region")
def get_sales_by_region(db: Session = Depends(get_db)):
    """Total revenue grouped by region."""
    query = text("""
        SELECT
            region,
            SUM(total_revenue) as total_revenue,
            SUM(total_orders) as total_orders,
            ROUND(AVG(avg_order_value)::numeric, 2) as avg_order_value
        FROM dbt_analytics.sales_summary
        GROUP BY region
        ORDER BY total_revenue DESC
    """)
    result = db.execute(query)
    return [dict(row) for row in result]


@app.get("/sales/monthly-trend")
def get_monthly_trend(
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Monthly revenue trend, optionally filtered by year."""
    query = "SELECT sale_year, sale_month, SUM(total_revenue) as total_revenue, SUM(total_orders) as total_orders FROM dbt_analytics.sales_summary"
    params = {}

    if year:
        query += " WHERE sale_year = :year"
        params["year"] = year

    query += " GROUP BY sale_year, sale_month ORDER BY sale_year, sale_month"

    result = db.execute(text(query), params)
    return [dict(row) for row in result]


@app.get("/sales/top-products")
def get_top_products(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Top products by total revenue from staged sales data."""
    query = text("""
        SELECT
            product,
            category,
            COUNT(*) as total_orders,
            SUM(quantity) as total_units_sold,
            ROUND(SUM(total_amount)::numeric, 2) as total_revenue
        FROM dbt_analytics.stg_sales
        GROUP BY product, category
        ORDER BY total_revenue DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    return [dict(row) for row in result]