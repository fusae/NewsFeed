from WeChatPush import WeChatPush
from collections import Counter
from TwitterBot import TwitterBot
import os
import json
import hashlib

DIR_PATH = os.getcwd()
CONFIG_NAME = os.path.join(DIR_PATH, "WeChat_Config.json")
DATA_DIR = os.path.join(DIR_PATH, "Data")
TWITTER_DATA_DIR = os.path.join(DATA_DIR, "Twitter")
FOLLOWING_COUNT_DIR = os.path.join(DATA_DIR, "Following_Count")

if not os.path.exists(FOLLOWING_COUNT_DIR):
	os.makedirs(FOLLOWING_COUNT_DIR)

#read file to get user_KOL_following
def get_user_KOL_following(userid):
    user_file = os.path.join(TWITTER_DATA_DIR, userid + ".json")
    with open(user_file) as f:
        data = json.load(f)

        return data

# according to the file, list the most common following, if the count bigger than 1 times, then send us message
def get_common_following(bot, userids):

    for userid in userids:
        #read file to get user_KOL_following
        user_KOL_following = get_user_KOL_following(userid)
            
        total_following = []
        # turn a big dict into a whole list
        for each_kol in user_KOL_following:
            total_following += user_KOL_following[each_kol]

        most_common = Counter(total_following).most_common()

        md5_list = []
        for each in most_common:
            if each[1] > 1:
                print(each[0])
                username = bot.get_user_name(each[0])
                handle = bot.get_user_username(each[0])
                count = each[1]

                content = {
                    "username": username,
                    "handle": handle,
                    "count": count
                }

                bot.wechatpush.send_message(content)

                # sign string as md5 string, and save it to local file, to avoid send repeatly
                md5_string = hashlib.md5((handle+str(count)).encode('utf-8')).hexdigest()
                md5_list.append(md5_string)

        data = {'md5': md5_list}
        user_file = os.path.join(FOLLOWING_COUNT_DIR, userid + ".json")

        with open(user_file, "w") as f:
            data = json.dumps(data)
            f.write(data)


if __name__ == '__main__':

    wechatpush = WeChatPush(file_path=CONFIG_NAME, type="Following_Count")

    bot = TwitterBot(wechatpush)

    userids = wechatpush.get_userids()

    get_common_following(bot, userids)