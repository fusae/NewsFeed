from NewsCollector import NewsCollector
from WeChatPush import WeChatPush
import os

DIR_PATH = os.getcwd()

# FILE_PATH = DIR_PATH + "\\WeChat_Config.json"

FILE_PATH = os.path.join(DIR_PATH, "WeChat_Config.json")

if __name__ == '__main__':

    wechatpush = WeChatPush(file_path=FILE_PATH, type="News")

    newsCollector = NewsCollector(wechatpush)

    # links = newsCollector.crawl_news()

    # for each in links:
    #     print(each)

    newsCollector.run() # only run one time

    print("Runing now...")
    