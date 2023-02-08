import os
from Utility.Email import Email
from datetime import datetime
import json
from Utility.NewsKeyword import NewsKeyword

DIR_PATH = os.getcwd()
CONFIG_FILE = os.path.join(DIR_PATH, "WeChat_Config.json")

DATA_DIR = os.path.join(DIR_PATH, "Data")
NEWS_DATA_DIR = os.path.join(DATA_DIR, "News")  # read

DATE = datetime.now().strftime("%Y-%m-%d")
DATE = '2023-02-08'

if __name__ == '__main__':

    email = Email()
    nk = NewsKeyword()

    print("running news email...")
    with open(CONFIG_FILE) as f:
        WeChat_Config = json.load(f)

    userids_emails = WeChat_Config["utility"]["NewsEmail"]["userids_emails"]

    for wechat_userid in userids_emails:
        read_user_dir = os.path.join(NEWS_DATA_DIR, wechat_userid)
        read_user_file = os.path.join(read_user_dir, DATE + ".json")

        titles = []
        with open(read_user_file) as f:
            data = json.load(f)
            NewsInfo = data['NewsInfo']

            i = 0
            for website in NewsInfo:
                for left in NewsInfo[website]:
                    title = nk.parse_news(website+left)
                    print("{}".format(i), title)
                    title = ("{} ".format(i)+title)
                    titles.append(title)
                    i += 1
        
        # send email
        email.send("News-"+DATE, '\n'.join(titles), userids_emails[wechat_userid])

    