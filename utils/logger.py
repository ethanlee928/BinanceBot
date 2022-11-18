import os
import logging


def get_logger(name):
    FORMAT = "[%(name)s] %(asctime)s %(levelname)s: %(message)s"
    LEVELS = [0, 10, 20, 30, 40, 50]
    level = int(os.getenv("LOG_LEVEL", logging.INFO))
    if level not in LEVELS:
        level = logging.INFO
    logger = logging.getLogger(name)
    logging.basicConfig(level=level, format=FORMAT)
    return logger


logger = get_logger(name="BinanceBot")
