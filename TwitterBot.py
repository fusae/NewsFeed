# This is a Twitter Bot, it would have these functions:
# 1. It would send WeChat message to us if a KOL follow a new project according to the KOL list
# 2. It would tweet automatically by giving the text, like funding news every day
# 3. It would like are retweet automatically by giving the tweet id
# 4. It would follow auotmatically by giving the user id

import tweepy
import os
import json
from WeChatPush import WeChatPush

DIR_PATH = os.getcwd()
CONFIG_NAME = os.path.join(DIR_PATH, "WeChat_Config.json") 
DATA_DIR = os.path.join(DIR_PATH, "Data")
TWITTER_DATA_DIR = os.path.join(DATA_DIR, "Twitter")

if not os.path.exists(TWITTER_DATA_DIR):
	os.makedirs(TWITTER_DATA_DIR)

class TwitterBot:
    def __init__(self, wechatpush):
        with open(CONFIG_NAME) as f:
            WeChat_Config = json.load(f)
            self.user_KOL_list = {}
            self.user_KOL_following = {} #read from file
            self.wechatpush = wechatpush


            self.client = tweepy.Client(
                consumer_key=WeChat_Config["type"]["Twitter"]["consumer_key"],
                consumer_secret=WeChat_Config["type"]["Twitter"]["consumer_secret"],
                access_token=WeChat_Config["type"]["Twitter"]["access_token"],
                access_token_secret=WeChat_Config["type"]["Twitter"]["access_token_secret"],
                bearer_token = WeChat_Config["type"]["Twitter"]["bearer_token"],
                wait_on_rate_limit=True
            )

            wechat_userids = WeChat_Config["type"]["Twitter"]["userids"]
            default_KOL_list = WeChat_Config["type"]["Twitter"]["default_KOL_list"]
            userid_fav = WeChat_Config["type"]["Twitter"]["userid_fav"]
            for wechat_userid in wechat_userids:
                self.user_KOL_following[wechat_userid] = {}
                self.user_KOL_list[wechat_userid] = default_KOL_list
                if wechat_userid in userid_fav:
                  self.user_KOL_list[wechat_userid] = userid_fav[wechat_userid]

            for wechat_userid in self.user_KOL_list:
                i = 0
                for username in self.user_KOL_list[wechat_userid]:
                    twitter_userid = self.get_user_id(username)
                    self.user_KOL_list[wechat_userid][i] = twitter_userid
                    i += 1

            # clear those unvalid ids, they are None
            for wechat_useid in self.user_KOL_list:
                i = 0
                for each in self.user_KOL_list[wechat_useid]:
                    if each is None:
                        del self.user_KOL_list[wechat_useid][i]
                    
                    i += 1


    # list the latest 10(default) following users' name by user id
    # return the list of user id and name and handle name
    def list_user_following(self, twitter_userid, max_results=10):
        print("Getting {0} following from {1}".format(str(max_results), twitter_userid))
        users = []
        response = self.client.get_users_following(twitter_userid, user_fields=["profile_image_url"], max_results=max_results)

        for user in response.data:
            print(user.id, user.name, user.username)
            users.append((user.id, user.name, user.username))

        return users

    def get_current_following(self, wechat_userid):
        user_file = os.path.join(TWITTER_DATA_DIR, wechat_userid + ".json")
        file_exists = self.if_file_exists(user_file, wechat_userid)
        following_dict = {}
        print("Get current following in {}".format(user_file))

        for twitter_userid in self.user_KOL_list[wechat_userid]:
            users = self.list_user_following(twitter_userid=twitter_userid)
            ids = []
            for user in users:
                ids.append(user[0])

            following_dict[str(twitter_userid)] = ids

        if not file_exists:
            # write data to file
            with open(user_file, "w") as f:
                data = json.dumps(following_dict)
                f.write(data)

        return following_dict

    def run(self):

        for wechat_userid in self.user_KOL_list:
            
            currrent_following = self.get_current_following(wechat_userid)
            # if self.user_KOL_following is empty, it means this is the first time run th program
            # it should be equal with the current_following
            if self.user_KOL_following[wechat_userid] == {}:
                self.user_KOL_following[wechat_userid] = currrent_following

            # compare each KOL's following ids (lateest 10)
            # To see what's new folloing user id in currrent_following
            for twitter_userid in self.user_KOL_list[wechat_userid]:
                new_following = list(set(currrent_following[str(twitter_userid)]).difference(self.user_KOL_following[wechat_userid][str(twitter_userid)]))

                if len(new_following) != 0:
                    for each in new_following:
                        print("{0} just followed {1}!".format(self.get_user_name(twitter_userid), self.get_user_name(each)))
                        # sned message
                        content = {
                            "kol": self.get_user_name(twitter_userid),
                            "username": self.get_user_name(each),
                            "handle": self.get_user_username(each),
                            "username_url": "https://twitter.com/" + self.get_user_username(each)
                        }

                        self.wechatpush.send_message(content, tousers=[twitter_userid])

                    # update currrent_following to local file
                    user_file = os.path.join(TWITTER_DATA_DIR, wechat_userid + ".json")
                    data = json.dumps(currrent_following)
                    with open(user_file, "w") as f:
                        f.write(data)

    # get user's handle name
    def get_user_username(self, twitter_userid):
        user = self.client.get_user(id=twitter_userid)
        return user.data['username']

    # get user's name
    def get_user_name(self, twitter_userid):
        user = self.client.get_user(id=twitter_userid)
        return user.data['name']

    # get user id by twitter handle
    def get_user_id(self, screen_name):
        user = self.client.get_user(username=screen_name)
        if user.data is None:
            return None

        twitter_userid = user.data['id']

        return twitter_userid

    def if_file_exists(self, file_name, wechat_userid):
        if os.path.exists(file_name):
            
            # read data from file
            f = open(file_name)
            data = json.load(f)
            print("Reading data in {}".format(file_name))
            self.user_KOL_following[wechat_userid] = data
            f.close()

            # should check if the amount of user ids are same between this file and config file
            # read data from Config file
            f = open(CONFIG_NAME)
            data = json.load(f)
            f.close()

            if len(self.user_KOL_following[wechat_userid]) != len(self.user_KOL_list[wechat_userid]):
                for each in self.user_KOL_list[wechat_userid]:
                    try:
                        ids = self.user_KOL_following[wechat_userid][str(each)]
                    except KeyError:
                        twitter_userid = each
                        users = self.list_user_following(twitter_userid=twitter_userid)
                        ids = []
                        for user in users:
                            ids.append(user[0])

                        self.user_KOL_following[wechat_userid][str(twitter_userid)] = ids


                for i in list(self.user_KOL_following[wechat_userid]):
                    if int(i) in self.user_KOL_list:
                        continue
                    else:
                        self.user_KOL_following[wechat_userid].pop(i)
                
                # update to local file
                with open(file_name, "w") as f:
                    data = json.dumps(self.user_KOL_following[wechat_userid])
                    f.write(data)

            return True

        else:
            # create a new blank file
            self.user_KOL_following[wechat_userid] = {}
            return False

if __name__ == '__main__':

    wechatpush = WeChatPush(file_path=CONFIG_NAME, type="Twitter")

    bot = TwitterBot(wechatpush)

    bot.run()