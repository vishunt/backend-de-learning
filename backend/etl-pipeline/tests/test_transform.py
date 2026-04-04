import pandas as pd
import pytest
from transform import transform


class TestTransformClean:

    def test_removes_zero_quantity(self, sample_raw_df):
        """Row with quantity=0 should be removed."""
        result = transform(sample_raw_df)
        assert all(result["quantity"] > 0)

    def test_calculates_total_amount(self, sample_raw_df):
        """total_amount should equal quantity * unit_price."""
        result = transform(sample_raw_df)
        for _, row in result.iterrows():
            expected = round(row["quantity"] * row["unit_price"], 2)
            assert round(row["total_amount"], 2) == expected

    def test_extracts_sale_month(self, sample_raw_df):
        """sale_month should be extracted from sale_date."""
        result = transform(sample_raw_df)
        assert set(result["sale_month"]).issubset(set(range(1, 13)))

    def test_extracts_sale_year(self, sample_raw_df):
        """sale_year should be extracted from sale_date."""
        result = transform(sample_raw_df)
        assert all(result["sale_year"] > 2000)

    def test_strips_and_titles_customer_name(self, sample_raw_df):
        """customer_name should be stripped and title-cased."""
        result = transform(sample_raw_df)
        for name in result["customer_name"]:
            assert name == name.strip()
            assert name == name.title()

    def test_titles_region(self, sample_raw_df):
        """region should be title-cased (north -> North)."""
        result = transform(sample_raw_df)
        for region in result["region"]:
            assert region == region.title()

    def test_removes_negative_price(self):
        """Rows with unit_price <= 0 should be removed."""
        df = pd.DataFrame({
            "customer_name": ["Alice"],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [1],
            "unit_price": [-10.0],
            "sale_date": pd.to_datetime(["2024-01-15"]),
            "region": ["North"],
            "ingested_at": pd.to_datetime(["2024-01-15"]),
        })
        result = transform(df)
        assert len(result) == 0

    def test_output_has_required_columns(self, sample_raw_df):
        """Transformed DataFrame must have all expected columns."""
        result = transform(sample_raw_df)
        required = ["total_amount", "sale_month", "sale_year", "transformed_at"]
        for col in required:
            assert col in result.columns

    def test_record_count_reduced_by_bad_rows(self, sample_raw_df):
        """One row has quantity=0 so output should have fewer rows than input."""
        result = transform(sample_raw_df)
        assert len(result) < len(sample_raw_df)