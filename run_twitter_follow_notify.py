import os
from Utility.WeChatPush import WeChatPush
from Utility.TwitterBot import TwitterBot

DIR_PATH = os.getcwd()
CONFIG_NAME = os.path.join(DIR_PATH, "WeChat_Config.json") 

if __name__ == '__main__':
    
    wechatpush = WeChatPush(file_path=CONFIG_NAME, type="Twitter")

    bot = TwitterBot(wechatpush)

    bot.run()