from celery_app import celery_app
import time

@celery_app.task
def process_book_added(book_id: int, title: str, author: str):
    """
    Simulates a background task when a book is added.
    In real life this could be: sending emails, updating search index, etc.
    """
    print(f"Processing book {book_id}: {title} by {author}")
    time.sleep(2)  # Simulate slow work
    print(f"Done processing book {book_id}")
    return {"status": "processed", "book_id": book_id}

@celery_app.task
def generate_books_report():
    """
    Simulates generating a report in the background.
    """
    print("Generating books report...")
    time.sleep(5)  # Simulate heavy processing
    print("Report generated!")
    return {"status": "report_generated"}