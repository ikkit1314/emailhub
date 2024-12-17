import logging
import os
from logging.handlers import RotatingFileHandler
from .config import LOG_FILE_PATH

# Setup logging
def setup_logger():
    logger = logging.getLogger("EmailParserLogger")
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if not exists
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    
    handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
