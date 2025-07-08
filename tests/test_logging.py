import logging
from core.log_utils import configure_logging


def test_logging_configuration(tmp_path):
    logging.getLogger().handlers.clear()
    logfile = tmp_path / "test.log"
    configure_logging(logfile=logfile)
    handlers = logging.getLogger().handlers
    assert handlers, "Logging not configured"
    fmt = handlers[0].formatter._fmt
    assert fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
