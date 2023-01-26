from requests_html import HTMLSession
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

DIR_PATH = os.getcwd()
CONFIG_FILE = os.path.join(DIR_PATH, "WeChat_Config.json")
DATA_DIR = os.path.join(DIR_PATH, "Data")
NEWS_DATA_DIR = os.path.join(DATA_DIR, "News")
NEWS_INFO_DIR = os.path.join(DATA_DIR, "NewsInfo")

DATE = datetime.now().strftime("%Y-%m-%d")

if not os.path.exists(NEWS_INFO_DIR):
	os.makedirs(NEWS_INFO_DIR)


class NewsKeyword:

    def __init__(self):

        with open(CONFIG_FILE) as f:
            WeChat_Config = json.load(f)

            self.wechat_userids = WeChat_Config["utility"]["NewsInfo"]["userids"]
            self.keywords = WeChat_Config["utility"]["NewsInfo"]["keywords"]
            
        self.session = HTMLSession()


    def parse_news(self, news_url):
        res = self.session.get(news_url)

        text = res.text

        soup = BeautifulSoup(text, "lxml")

        title = soup.title

        if title is None:
            return "No title"

        title = title.text

        return title

    # get specific news according keyword in a single data file
    def get_news_from_keyword(self, wechat_userid):
        
        read_user_file = os.path.join(NEWS_DATA_DIR, wechat_userid + ".json")
       
        # to store the matched title
        keywords_title = {}
        for keyword in self.keywords:
            keywords_title[keyword] = []


        with open(read_user_file) as f:
            data = json.load(f)
            NewsInfo = data["NewsInfo"]

            i = 0
            for each in NewsInfo:
                if each['date'] == DATE:
                    title = self.parse_news(each["url"])
                    print("{}".format(i), title)
                    i += 1
                    for keyword in self.keywords:
                        if keyword in title:
                            keywords_title[keyword].append(title)
                            print("符合关键词，加入队列")

        # write data to file
        write_user_dir = os.path.join(NEWS_INFO_DIR, wechat_userid)
        if not os.path.exists(write_user_dir):
            os.makedirs(write_user_dir)

        for keyword in keywords_title:
            write_user_file = os.path.join(write_user_dir, keyword + '-' + DATE + '.json')
            with open(write_user_file, "w") as f:
                data = json.dumps(keywords_title[keyword], ensure_ascii=False)
                f.write(data)

if __name__ == '__main__':

    nk = NewsKeyword()

    with open(CONFIG_FILE) as f:
            WeChat_Config = json.load(f)
            
    wechat_userid = WeChat_Config["utility"]["NewsInfo"]["userids"][0]

    nk.get_news_from_keyword(wechat_userid)

        




    