import os
from datetime import datetime
import json
from Utility.Email import Email

DIR_PATH = os.getcwd()
LOG_DIR = os.path.join(DIR_PATH, "Log")

DATE = datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":

    email = Email()

    with open(os.path.join(LOG_DIR, '{:%Y-%m-%d}.log'.format(datetime.now()))) as f:
        data = f.read()

    # send email
    email.send("关注通知-"+DATE, data)