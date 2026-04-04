from extract import create_tables, seed_raw_data
from transform import extract_raw_data, transform, load_transformed
from validate import validate_transformed_data
from logger import get_logger
from datetime import datetime

logger = get_logger("pipeline")


def run_pipeline():
    start_time = datetime.utcnow()
    logger.info("=" * 50)
    logger.info(f"ETL Pipeline started at {start_time}")
    logger.info("=" * 50)

    # Step 1 - Extract
    logger.info("STEP 1: Extract — creating tables and seeding data")
    create_tables()
    seed_raw_data(n=200)
    logger.info("Extract complete.")

    # Step 2 - Transform
    logger.info("STEP 2: Transform — reading, cleaning, loading")
    raw = extract_raw_data()
    logger.info(f"Raw records extracted: {len(raw)}")
    transformed = transform(raw)
    logger.info(f"Records after transform: {len(transformed)}")
    load_transformed(transformed)
    logger.info("Transform complete.")

    # Step 3 - Validate
    logger.info("STEP 3: Validate — running schema checks")
    passed = validate_transformed_data()