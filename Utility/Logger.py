import logging
import os
from datetime import datetime

DIR_PATH = os.getcwd()
LOG_DIR = os.path.join(DIR_PATH, "Log")

if not os.path.exists(LOG_DIR):
    	os.makedirs(LOG_DIR)

class Logger:
    def __init__(self):
        # Create a custom logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create a file handler
        f_handler = logging.FileHandler(os.path.join(LOG_DIR, '{:%Y-%m-%d}.log'.format(datetime.now())), encoding='utf-8')

        # Create fomatter and add it to handler
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        f_handler.setFormatter(f_format)

        self.logger.addHandler(f_handler)

    def getLogger(self):
        return self.logger