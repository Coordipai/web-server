# logger_config.py
import logging
import logging.handlers
import os
from datetime import datetime

import colorlog


def setup_logger(name):
    """
    Sets and returns a logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set logging level

    # Console handler (print color)
    console_handler = logging.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def add_daily_file_handler(logger, log_dir="logs"):
    """
    Add a handler to the logger to save to a file by date.
    """
    # Create log directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a date-based file logging handler
    log_file_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when="D",  # Create new files every day
        interval=1,  # 1 day interval
        backupCount=7,  # Keep 7 days worth of log files
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    daily_handler.setFormatter(file_formatter)
    logger.addHandler(daily_handler)
