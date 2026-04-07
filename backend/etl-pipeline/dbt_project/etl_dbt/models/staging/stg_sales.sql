-- models/staging/stg_sales.sql
-- Staging model: clean view of transformed_sales
-- This is the base layer — minimal transformations, just renaming and typing

with source as (
    select * from {{ source('etl', 'transformed_sales') }}
),

staged as (
    select
        id,
        customer_name,
        product,
        category,
        quantity,
        unit_price,
        total_amount,
        region,
        sale_date,
        sale_month,
        sale_year,
        transformed_at
    from source
    where quantity > 0
      and unit_price > 0
      and total_amount > 0
)

select * from staged