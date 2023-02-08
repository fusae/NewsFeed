import os
import smtplib
from email.mime.text import MIMEText
import json

DIR_PATH = os.getcwd()
CONFIG_FILE = os.path.join(DIR_PATH, "WeChat_Config.json")

class Email:
    def __init__(self):
        pass

    def send(self, subject, content, receivers=[]):

        with open(CONFIG_FILE, encoding= 'utf-8') as f:
            WeChat_Config = json.load(f)

        self.email = WeChat_Config["utility"]["NewsInfo"]["email"]
        self.client = smtplib.SMTP_SSL(self.email["host"], 465)
        self.client.login(self.email["user"], self.email["password"])

        msg = MIMEText(content, 'plain', 'utf-8')
        msg["From"] = self.email["sender"]
        if len(receivers) == 0:
            receivers = self.email["receivers"]
        msg['to'] = ",".join(receivers)
        msg["Subject"] = subject

        try:
            self.client.sendmail(self.email["sender"], self.email["receivers"], msg.as_string())
            print("Mail has been send sucessfully")
            
        except smtplib.SMTPException as e:
            print(e)
