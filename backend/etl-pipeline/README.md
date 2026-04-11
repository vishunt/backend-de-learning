# ETL Data Pipeline

A production-style ETL (Extract, Transform, Load) data pipeline built with Python, pandas, Pandera, Apache Airflow, and dbt. Includes a FastAPI query layer for serving analytics data.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python + pandas | Data extraction and transformation |
| Pandera | Data validation and schema enforcement |
| SQLAlchemy | Database interaction |
| Apache Airflow | Pipeline orchestration and scheduling |
| dbt (data build tool) | Analytics models and data transformation |
| FastAPI | Query layer API on top of dbt models |
| PostgreSQL | Data warehouse |
| Docker Compose | Airflow containerization |
| pytest | 15 tests covering transform and validation logic |

## Architecture

Raw Data (Faker)
→ extract.py (seed PostgreSQL raw_sales table)
→ transform.py (pandas cleaning + derived columns)
→ validate.py (Pandera schema checks)
→ load.py (pipeline orchestrator)
→ Airflow DAG (daily scheduling)
→ dbt models (staging + marts analytics layer)
→ Query API (FastAPI endpoints on dbt output)

## Project Structure

etl-pipeline/
├── src/
│   ├── extract.py      # SQLAlchemy models + Faker seed data
│   ├── transform.py    # pandas cleaning and transformation
│   ├── validate.py     # Pandera schema validation
│   ├── load.py         # Pipeline runner with logging
│   └── logger.py       # Timestamped file + console logging
├── tests/
│   ├── test_transform.py   # 9 transform tests
│   └── test_validate.py    # 6 validation tests
├── airflow/
│   ├── dags/etl_dag.py     # Airflow DAG (3 tasks, @daily)
│   └── docker-compose.yml  # Airflow webserver + scheduler
├── dbt_project/etl_dbt/
│   ├── models/staging/stg_sales.sql       # Cleaned view
│   ├── models/marts/sales_summary.sql     # Aggregated table
│   └── models/staging/schema.yml          # 7 dbt tests
└── query-api/
└── main.py     # FastAPI with 5 analytics endpoints

## Pipeline Steps

**1. Extract** — Generates realistic fake sales data using Faker and seeds it into the `raw_sales` PostgreSQL table using SQLAlchemy bulk inserts.

**2. Transform** — Reads raw data into a pandas DataFrame, removes nulls and duplicates, enforces data types, derives `total_amount`, `sale_month`, and `sale_year`, standardizes string fields, and filters out invalid records.

**3. Validate** — Pandera schema checks every row in `transformed_sales` for type correctness, value ranges, and allowed values (e.g. region must be North/South/East/West, sale_month must be 1–12).

**4. Load** — Orchestrates all three steps with logging. Every pipeline run writes a timestamped log file.

**5. Airflow** — A DAG with 3 PythonOperator tasks runs the pipeline on a @daily schedule. Managed via Docker Compose.

**6. dbt** — Two models built on top of transformed data:
- `stg_sales` (view) — clean staging layer
- `sales_summary` (table) — aggregated by category, region, month, year

**7. Query API** — FastAPI app exposing dbt analytics data via REST endpoints.

## Quick Start

```bash
# Start PostgreSQL (shared with task-management-api)
cd ../task-management-api && docker compose up -d

# Activate virtual environment
cd ../etl-pipeline
.venv\Scripts\activate  # Windows

# Run the pipeline
cd src && python load.py

# Run tests
cd .. && pytest -v

# Start Airflow
cd airflow && docker compose up -d

# Run dbt models
cd ../dbt_project/etl_dbt && dbt run && dbt test

# Start Query API
cd ../../query-api && uvicorn main:app --reload --port 8001
```

## Query API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /sales/summary | Full summary with optional filters |
| GET | /sales/by-category | Revenue grouped by category |
| GET | /sales/by-region | Revenue grouped by region |
| GET | /sales/monthly-trend | Monthly revenue trend |
| GET | /sales/top-products | Top N products by revenue |

## Test Coverage

- **15 tests** across transform and validation logic
- Tests run with in-memory DataFrames — no database required
- Covers: null removal, bad data filtering, derived column calculations, Pandera schema enforcement, edge cases