import logging
from config import LOGGING_ENABLED, LOGGING_LEVEL, LOG_FILE

def setup_logger():
    if LOGGING_ENABLED:
        logging.basicConfig(
            level=getattr(logging, LOGGING_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)  # فقط لاگ‌های بحرانی را نمایش می‌دهد

def get_logger(name):
    setup_logger()
    return logging.getLogger(name)
