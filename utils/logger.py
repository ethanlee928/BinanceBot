import os
import logging

def get_logger(name):
    FORMAT = '[%(name)s] %(asctime)s %(levelname)s: %(message)s'
    LEVELS = [0, 10, 20, 30, 40, 50]
    level = int(os.getenv('LOG_LEVEL', logging.INFO))
    if level not in LEVELS:
        level = logging.INFO
    logger = logging.getLogger(name)
    logging.basicConfig(level=level, format=FORMAT)
    return logger

if __name__ == "__main__":

    log = get_logger(name='tester')
    log.debug('DEBUG message')
    log.info('INFO message')
    log.warning('WARNING message')
    log.error('ERROR message')
    log.critical('CRITICAL message')
    