from pydantic import BaseModel
from typing import Optional


class SalesSummary(BaseModel):
    category: str
    region: str
    sale_year: int
    sale_month: int
    total_orders: int
    total_units_sold: int
    total_revenue: float
    avg_order_value: float
    avg_unit_price: float

    class Config:
        from_attributes = True


class StagedSale(BaseModel):
    id: Optional[int]
    customer_name: Optional[str]
    product: Optional[str]
    category: Optional[str]
    quantity: Optional[int]
    unit_price: Optional[float]
    total_amount: Optional[float]
    region: Optional[str]
    sale_month: Optional[int]
    sale_year: Optional[int]

    class Config:
        from_attributes = True