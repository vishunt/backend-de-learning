import pytest
import pandas as pd
import pandera as pa
from validate import transformed_schema


class TestValidationSchema:

    def test_valid_data_passes(self):
        """A clean DataFrame should pass all validation checks."""
        df = pd.DataFrame({
            "customer_name": ["Alice Smith", "Bob Jones"],
            "product": ["Laptop", "Phone"],
            "category": ["Electronics", "Electronics"],
            "quantity": [2, 3],
            "unit_price": [999.99, 299.99],
            "total_amount": [1999.98, 899.97],
            "sale_month": [1, 3],
            "sale_year": [2024, 2024],
            "region": ["North", "South"],
            "sale_date": pd.to_datetime(["2024-01-15", "2024-03-20"]),
            "ingested_at": pd.to_datetime(["2024-01-15", "2024-03-20"]),
            "transformed_at": pd.to_datetime(["2024-01-15", "2024-03-20"]),
        })
        # Should not raise
        transformed_schema.validate(df, lazy=True)

    def test_negative_quantity_fails(self, bad_df):
        """Negative quantity should fail validation."""
        with pytest.raises(pa.errors.SchemaErrors):
            transformed_schema.validate(bad_df, lazy=True)

    def test_invalid_region_fails(self, bad_df):
        """Invalid region value should fail validation."""
        with pytest.raises(pa.errors.SchemaErrors):
            transformed_schema.validate(bad_df, lazy=True)

    def test_invalid_month_fails(self, bad_df):
        """sale_month outside 1-12 should fail validation."""
        with pytest.raises(pa.errors.SchemaErrors):
            transformed_schema.validate(bad_df, lazy=True)

    def test_valid_regions_accepted(self):
        """All four valid regions should pass."""
        for region in ["North", "South", "East", "West"]:
            df = pd.DataFrame({
                "customer_name": ["Alice"],
                "product": ["Laptop"],
                "category": ["Electronics"],
                "quantity": [1],
                "unit_price": [99.99],
                "total_amount": [99.99],
                "sale_month": [6],
                "sale_year": [2024],
                "region": [region],
                "sale_date": pd.to_datetime(["2024-06-01"]),
                "ingested_at": pd.to_datetime(["2024-06-01"]),
                "transformed_at": pd.to_datetime(["2024-06-01"]),
            })
            transformed_schema.validate(df, lazy=True)

    def test_all_months_valid(self):
        """Months 1 through 12 should all pass."""
        for month in range(1, 13):
            df = pd.DataFrame({
                "customer_name": ["Alice"],
                "product": ["Laptop"],
                "category": ["Electronics"],
                "quantity": [1],
                "unit_price": [99.99],
                "total_amount": [99.99],
                "sale_month": [month],
                "sale_year": [2024],
                "region": ["North"],
                "sale_date": pd.to_datetime(["2024-06-01"]),
                "ingested_at": pd.to_datetime(["2024-06-01"]),
                "transformed_at": pd.to_datetime(["2024-06-01"]),
            })
            transformed_schema.validate(df, lazy=True)