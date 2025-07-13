"""Example plugin used for tests and documentation."""

import logging

from core.log_utils import configure_logging


def run() -> None:
    configure_logging()
    logging.info("Example plugin executed")
