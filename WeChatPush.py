import requests
import json
from threading import Timer
from datetime import datetime, timedelta
import os
import os.path

DIR_PATH = os.getcwd()

ACCESS_TOKEN_PATH = os.path.join(DIR_PATH, "ACCESS_TOKEN.json")

class WeChatPush:

    def __init__(self, file_path, type) -> None:
        
        f = open(file_path)
        WeChat_Config = json.load(f)

        self.appid = WeChat_Config['appid']
        self.appsecret = WeChat_Config['appsecret']
        self.access_token = None
        self.userids = WeChat_Config["type"][type]['userids']
        self.template_id = WeChat_Config["type"][type]["template_id"]
        self.type = type

        # self.access_token = self.get_access_token()
        self.handle_access_token()

        f.close()

    def get_userids(self):
        return self.userids

    def cal_expired_time(self, hours=2):
        expired_time = datetime.now() + timedelta(hours=hours)
        return expired_time.strftime("%Y-%m-%d %H:%M:%S")

    def is_access_token_expired(self, expired_time):
        
        with open(ACCESS_TOKEN_PATH, "r") as f:
            content = json.load(f)

            expected_expired_time = content['expired_time']

            expected_expired_time = datetime.strptime(expected_expired_time, "%Y-%m-%d %H:%M:%S")
            expired_time = datetime.strptime(expired_time, "%Y-%m-%d %H:%M:%S")

            if expired_time > expected_expired_time:
                return True
            else:
                return False

    def handle_access_token(self):
        
        # Check if the file exist
        file_exist = os.path.exists(ACCESS_TOKEN_PATH)

        if file_exist:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.is_access_token_expired(expired_time=now):
                self.access_token = self.get_access_token()
                expired_time = self.cal_expired_time()
                content = {
                    "access_token": self.access_token,
                    "expired_time": expired_time
                }

                content = json.dumps(content)

                with open(ACCESS_TOKEN_PATH, "w") as f:
                    f.write(content)

            else:
                with open(ACCESS_TOKEN_PATH) as f:
                    content = json.load(f)
                    self.access_token = content['access_token']
        else:
            self.access_token = self.get_access_token()
            expired_time = self.cal_expired_time()
            content = {
                "access_token": self.access_token,
                "expired_time": expired_time
            }

            content = json.dumps(content)
            with open(ACCESS_TOKEN_PATH, "w") as f:
                f.write(content)                

        # if not, createt one and call get_access_token() and write it into file

        # if the file exist, need to check the exipired_time variable, another if-else statement

     
    def get_access_token(self):
        
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(self.appid, self.appsecret)

        res = requests.get(url)

        text = json.loads(res.text)

        return text['access_token'] # available within 2 hours

        # Timer(60 * 60 * 2, self.get_access_token).start()

    def send_message(self, content, tousers=[]):

        # if tousers is empty, then defauly tousers is self.userids
        if len(tousers) == 0:
            tousers = self.userids

        if self.type == "News":
            title = content['title']
            news_url = content['news_url']

            data = {
                "title": {
                    "value": title,
                    "color": "#173177"
                }
            }

            for userid in tousers:
                post_data = {
                    "touser": userid,
                    "template_id": self.template_id,
                    "topcolor": "#FF0000",
                    "data": data,
                    "url": news_url
                }

                # call send_message_with_userid function
                errmsg = self.send_message_with_userid(post_data)
                print(errmsg)

        elif self.type == "Twitter":

            data = {
                "kol": {
                    "value": content["kol"]
                },
                "username": {
                    "value": content["username"] + '(@' + content['handle'] + ')'
                }
            }

            for userid in tousers:
                post_data = {
                    "touser": userid,
                    "template_id": self.template_id,
                    "topcolor": "#FF0000",
                    "url": content["username_url"],
                    "data": data
                }

                # call send_message_with_userid function
                errmsg = self.send_message_with_userid(post_data)
                print(errmsg)

        elif self.type == "Following_Count":

            data = {
                "username": {
                    "value": content["username"]
                },
                "handle": {
                    "value": content["handle"]
                },
                "count": {
                    "value": content["count"]
                }
            }

            for userid in tousers:
                post_data = {
                    "touser": userid,
                    "template_id": self.template_id,
                    "topcolor": "#FF0000",
                    "data": data
                }

                # call send_message_with_userid function
                errmsg = self.send_message_with_userid(post_data)
                print(errmsg)

    def send_message_with_userid(self, data):

        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(self.access_token)

        data = json.dumps(data)
        res = requests.post(url, data=data)

        text = json.loads(res.text)
        
        return text["errmsg"]


if __name__ == '__main__':

    file_path = "/Users/jamesyu/Documents/Codes/NewsFeed/WeChat_Config.json"
    wechatpush = WeChatPush(file_path=file_path)

    content = {
        "title": "this is a test title",
        "news_url": "https://zendaily.xyz/p/zendaily-27th-dec-2022"
    }

    wechatpush.send_message(content=content)