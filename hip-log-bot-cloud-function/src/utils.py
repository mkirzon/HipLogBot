import os
import logging
from datetime import datetime


def is_valid_date_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_runtime_config():
    runtime_env = os.getenv("ENVIRONMENT", "local")

    # Determine the logging level based on the environment
    if runtime_env == "local":
        log_level = logging.DEBUG
    elif runtime_env == "test":
        log_level = logging.DEBUG
    elif runtime_env == "production":
        log_level = logging.INFO
    else:
        log_level = logging.WARNING  # default

    return {"log_level": log_level}


# Constants
test_username = "MarkTheTester"
