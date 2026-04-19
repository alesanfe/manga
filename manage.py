#!/usr/bin/env python
"""
Copyright (c) 2019 - present Manga Project
"""

import os
import sys

# Import centralized logger configuration
from utils.logger_config import logger


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    logger.info(f"Starting Django with command: {' '.join(sys.argv)}")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error("Django import error")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    logger.info("Django command completed")

if __name__ == '__main__':
    main()
