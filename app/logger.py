import logging

from pythonjsonlogger import jsonlogger

from app.settings import settings


def get_logger():
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, getattr(settings, "LOG_LEVEL"))
    logger.setLevel(log_level)
    sh = logging.StreamHandler()
    sh.setFormatter(jsonlogger.JsonFormatter())
    sh.setLevel(log_level)
    logger.addHandler(sh)
    return logger


logger = get_logger()
