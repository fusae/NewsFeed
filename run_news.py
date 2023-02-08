from Utility.NewsCollector import NewsCollector
from Utility.WeChatPush import WeChatPush
import os

DIR_PATH = os.getcwd()
FILE_PATH = os.path.join(DIR_PATH, "WeChat_Config.json")

if __name__ == '__main__':

    wechatpush = WeChatPush(file_path=FILE_PATH, type="News")

    newsCollector = NewsCollector(wechatpush)

    newsCollector.run() # only run one time

    print("Runing News now...")
    