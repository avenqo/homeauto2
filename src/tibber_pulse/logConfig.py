import logging
from logging.handlers import RotatingFileHandler
import sys

LOG_FILE = './logs/info.log'

# number of rotating log files created
MAX_FILE_CNT = 10
# in kB
MAX_FILE_SIZE = 1024


def initLogger():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger("Rotating Multiplus Control")
    log.setLevel(logging.INFO)
    # log.setLevel(logging.DEBUG)
    # Rotating Handler
    rotatingHandler = RotatingFileHandler(
        LOG_FILE, maxBytes=(MAX_FILE_SIZE * 1024), backupCount=MAX_FILE_CNT)
    rotatingHandler.setFormatter(formatter)
    log.addHandler(rotatingHandler)
    # Console out handler
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)
    log.addHandler(consoleHandler)
    return log
