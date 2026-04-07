-- models/marts/sales_summary.sql
-- Mart model: aggregated sales summary by category and region
-- This is what analysts and dashboards would query

with staged as (
    select * from {{ ref('stg_sales') }}
),

summary as (
    select
        category,
        region,
        sale_year,
        sale_month,
        count(*)                        as total_orders,
        sum(quantity)                   as total_units_sold,
        round(sum(total_amount)::numeric, 2)  as total_revenue,
        round(avg(total_amount)::numeric, 2)  as avg_order_value,
        round(avg(unit_price)::numeric, 2)    as avg_unit_price
    from staged
    group by
        category,
        region,
        sale_year,
        sale_month
)

select * from summary
order by sale_year, sale_month, total_revenue desc