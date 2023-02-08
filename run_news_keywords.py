import os
import json
from datetime import datetime
from Utility.Email import Email
from Utility.NewsKeyword import NewsKeyword
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIR_PATH = os.getcwd()
CONFIG_FILE = os.path.join(DIR_PATH, "WeChat_Config.json")
DATA_DIR = os.path.join(DIR_PATH, "Data")
NEWS_INFO_DIR = os.path.join(DATA_DIR, "NewsInfo") # write

DATE = datetime.now().strftime("%Y-%m-%d")

if not os.path.exists(NEWS_INFO_DIR):
	os.makedirs(NEWS_INFO_DIR)

if __name__ == '__main__':

    nk = NewsKeyword()
    email = Email()

    with open(CONFIG_FILE) as f:
        WeChat_Config = json.load(f)
            
    wechat_userids = WeChat_Config["utility"]["NewsInfo"]["userids"]

    for wechat_userid in wechat_userids:
        keywords_title = nk.get_news_from_keyword(wechat_userid)

        for keyword in keywords_title:
            email.send(keyword+'-'+DATE, '\n'.join(keywords_title[keyword]))



    