import logging
import os
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """
    Creates a logger that writes to both the console and a log file.
    Each pipeline run gets its own timestamped log file in the logs/ folder.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Format: timestamp - logger name - level - message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — prints to terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler — writes to logs/ folder
    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger