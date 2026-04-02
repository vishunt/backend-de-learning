from extract import create_tables, seed_raw_data
from transform import extract_raw_data, transform, load_transformed
from validate import validate_transformed_data
from datetime import datetime


def run_pipeline():
    print(f"\n{'='*50}")
    print(f"ETL Pipeline started at {datetime.utcnow()}")
    print(f"{'='*50}\n")

    # Step 1 - Extract
    print("STEP 1: Extract")
    create_tables()
    seed_raw_data(n=200)

    # Step 2 - Transform
    print("\nSTEP 2: Transform")
    raw = extract_raw_data()
    transformed = transform(raw)
    load_transformed(transformed)

    # Step 3 - Validate
    print("\nSTEP 3: Validate")
    passed = validate_transformed_data()

    print(f"\n{'='*50}")
    if passed:
        print("Pipeline completed SUCCESSFULLY.")
    else:
        print("Pipeline completed with VALIDATION ERRORS.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_pipeline()