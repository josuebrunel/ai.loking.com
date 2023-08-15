import logging

from jsonformatter import JsonFormatter

from app.settings import settings


def get_logger():
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, getattr(settings, "LOG_LEVEL"))
    logger.setLevel(log_level)
    sh = logging.StreamHandler()
    formatter = JsonFormatter(
        fmt='''{
            "asctime": "asctime",
            "name": "name",
            "levelname": "levelname",
            "pathname": "pathname",
            "lineno": "lineno",
            "funcName": "funcName",
            "message": "message"
        }''',
        mix_extra=True,
        mix_extra_position="tail",
    )
    sh.setFormatter(formatter)
    sh.setLevel(log_level)
    logger.addHandler(sh)
    return logger


logger = get_logger()
