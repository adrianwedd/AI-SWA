"""Example usage of the Rust Bridge service."""

import logging

from .bridge_client import reverse
from .log_utils import configure_logging


def example() -> None:
    configure_logging()
    text = "abc"
    logging.info("Reversed: %s", reverse(text))


if __name__ == "__main__":
    example()
