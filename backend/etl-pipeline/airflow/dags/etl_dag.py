from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add the ETL source code to Python path so we can import it
sys.path.insert(0, '/opt/airflow/etl_src')

# Set DATABASE_URL explicitly for the Airflow container
os.environ["DATABASE_URL"] = "postgresql://postgres:password@host.docker.internal:5433/etl_db"

from extract import create_tables, seed_raw_data
from transform import extract_raw_data, transform, load_transformed
from validate import validate_transformed_data

# Default arguments applied to all tasks in the DAG
default_args = {
    'owner': 'vishnu',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
}

def extract_task():
    """Step 1 — Create tables and seed raw data."""
    create_tables()
    seed_raw_data(n=50)
    print("Extract complete.")

def transform_task():
    """Step 2 — Read raw data, clean it, load to transformed table."""
    raw = extract_raw_data()
    transformed = transform(raw)
    load_transformed(transformed)
    print(f"Transform complete. {len(transformed)} records loaded.")

def validate_task():
    """Step 3 — Validate the transformed data against schema."""
    passed = validate_transformed_data()
    if not passed:
        raise ValueError("Validation failed — pipeline stopped.")
    print("Validation passed.")

# Define the DAG
with DAG(
    dag_id='etl_pipeline',
    description='ETL pipeline — extract, transform, validate sales data',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',    # run once per day
    catchup=False,                 # don't backfill missed runs
    tags=['etl', 'sales'],
) as dag:

    t1 = PythonOperator(
        task_id='extract',
        python_callable=extract_task,
    )

    t2 = PythonOperator(
        task_id='transform',
        python_callable=transform_task,
    )

    t3 = PythonOperator(
        task_id='validate',
        python_callable=validate_task,
    )

    # Define order: extract -> transform -> validate
    t1 >> t2 >> t3