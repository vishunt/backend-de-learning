from celery_app import celery_app
from logger import get_logger

logger = get_logger("celery")

@celery_app.task
def send_task_created_notification(task_id: int, title: str, owner_username: str):
    """
    Simulates sending a notification when a task is created.
    In production: send email, push notification, Slack message etc.
    """
    logger.info(f"Sending notification for task {task_id}: '{title}' by {owner_username}")
    # Simulate work
    import time
    time.sleep(1)
    logger.info(f"Notification sent for task {task_id}")
    return {"status": "notification_sent", "task_id": task_id}

@celery_app.task
def send_task_completed_notification(task_id: int, title: str):
    """
    Simulates sending a notification when a task is completed.
    """
    logger.info(f"Task {task_id} completed: '{title}'")
    import time
    time.sleep(1)
    logger.info(f"Completion notification sent for task {task_id}")
    return {"status": "completion_notified", "task_id": task_id}