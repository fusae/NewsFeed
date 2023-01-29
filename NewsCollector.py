from requests_html import HTMLSession
from bs4 import BeautifulSoup
import os.path
import json
import os
from datetime import datetime

DIR_PATH = os.getcwd()

CONFIG_FILE = os.path.join(DIR_PATH, "WeChat_Config.json")
DATA_DIR = os.path.join(DIR_PATH, "Data")
NEWS_DATA_DIR = os.path.join(DATA_DIR, "News")

if not os.path.exists(NEWS_DATA_DIR):
	os.makedirs(NEWS_DATA_DIR)

DATE = datetime.now().strftime("%Y-%m-%d")

class NewsCollector:
	
	def __init__(self, wechatpush) -> None:
		
		# read from file
		with open(CONFIG_FILE) as f:
			WeChat_Config = json.load(f)
			
			# assign default urls to every user
			# and assign fav urls to every user who want to be special
			self.news_urls = {}
			self.userid_urls = {}
			self.userids = wechatpush.get_userids()
			default_urls = WeChat_Config["type"]["News"]["default_urls"]
			self.watch_urls = WeChat_Config["type"]["News"]["watch_urls"]
			userid_fav = WeChat_Config["type"]["News"]["userid_fav"]
			for userid in self.userids:
				self.news_urls[userid] = []
				self.userid_urls[userid] = default_urls
				if userid in userid_fav:
					self.userid_urls[userid] = userid_fav[userid]


		self.session = HTMLSession()

		self.wechatpush = wechatpush
		

		self.crawl_news() # add those old news to self.news_urls

	def has_numbers(self, inputString):
		return any(char.isdigit() for char in inputString)

	def if_file_exists(self, userid):

		# if the user_id dir not created, then create a new one
		user_dir = os.path.join(NEWS_DATA_DIR, userid)
		if not os.path.exists(user_dir):
			os.makedirs(user_dir)
		
		# Only check the day's news
		file_name = os.path.join(user_dir, DATE+".json")
		if os.path.exists(file_name):
			
			# read f from file
			f = open(file_name)
			data = json.load(f)

			links = []
			for each in data["NewsInfo"]:
				for left in data["NewsInfo"][each]:
					links.append(each+left)
			self.news_urls[userid] = links
			f.close()
			return True

		else:
			# create a new blank file
			return False

	def parse_news(self, news_url):
		res = self.session.get(news_url)

		text = res.text

		soup = BeautifulSoup(text, "lxml")

		title = soup.title

		if title is None:
			return "No title"
		
		title = title.text

		return title

	def crawl_news(self):
	# lookup every user by wechatID
	# crawl news to see if this news new or old
	# if this news is new, then we add it to links
	# if this news is old, then we ignore it
		userlinks = {}
		for userid in self.userids:

			file_exists = self.if_file_exists(userid)

			# init NewsInfo and NewsInfo_in_file
			# NewsInfo is the dict of self.news_urls(which is a list), key is website's name
			# NewsInfo_in_file is the dict of the file, which is a dict, compare to new news
			NewsInfo = {}
			NewsInfo_in_file = {}
			for each in self.watch_urls:
				NewsInfo[each] = []
				NewsInfo_in_file[each] = []

			news_urls = {}
	
			for each in self.news_urls[userid]:
				for key in NewsInfo_in_file:
					if key in each:
						left = each.replace(key, "")
						NewsInfo_in_file[key].append(left)
			news_urls[userid] = NewsInfo_in_file

			for each in self.userid_urls[userid]:
				res = self.session.get(each)
				absolute_links = res.html.absolute_links

				for link in absolute_links:

					if "https://zendaily.xyz/p/" in link and "comments" not in link:
						
						website = "https://zendaily.xyz/p/"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new zendaily post")
							NewsInfo[website].append(left)

					elif "https://www.theblockbeats.info" in link and "search" not in link and self.has_numbers(link):
						
						website = "https://www.theblockbeats.info"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new blockbeats post")
							NewsInfo[website].append(left)

					elif "https://en.bitpush.news/articles" in link and "tag" not in link:

						website = "https://en.bitpush.news/articles"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new bitpush post")
							NewsInfo[website].append(left)

					elif "https://nftevening.com" in link and "respond" not in link:

						website = "https://nftevening.com"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new nftevening post")
							NewsInfo[website].append(left)

					elif "https://newsbtc.com/news/" in link and '-' in link:

						website = "https://newsbtc.com/news/"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new newsbtc post")
							left = link.split(website)[1]
							NewsInfo[website].append(left)

					elif 'articledetails' in link or 'sqarticledetails' in link:
						
						website = "https://www.panewslab.com/zh/"
						left = link.split(website)[1]
						if left not in news_urls[userid][website]:
							print("Found new panewslab post")
							NewsInfo[website].append(left)

			links = []
			if file_exists:
				for each in NewsInfo:
					for left in NewsInfo[each]:
						links.append(each+left)
				userlinks[userid] = links
			else:
				
				data = {
					"NewsInfo": NewsInfo
				}

				data = json.dumps(data)

				user_dir = os.path.join(NEWS_DATA_DIR, userid)
				user_file = os.path.join(user_dir, DATE+".json")
				with open(user_file, "w") as f:
					f.write(data)

				self.news_urls[userid] = links

				userlinks[userid] =[]

		return userlinks


	def run(self):
			
		new_links = self.crawl_news()
		for userid in new_links:
			for each in new_links[userid]:
				if each in self.news_urls[userid]:
					continue

				else:
					print("Add new post")

					# call NewsFeed
					url = each
					title = self.parse_news(url)

					content = {
						"title": title,
						"news_url": url
					}

					self.wechatpush.send_message(content)

					self.news_urls[userid].append(each)

			# Update file
			NewsInfo = {}
			for each in self.watch_urls:
				NewsInfo[each] = []

			for each in self.news_urls[userid]:
				for key in NewsInfo:
					if key in each:
						left = each.replace(key, "")
						NewsInfo[key].append(left)

			data = {
				"NewsInfo": NewsInfo
			}
			data = json.dumps(data)
			user_dir = os.path.join(NEWS_DATA_DIR, userid)
			user_file = os.path.join(user_dir, DATE+".json")
			with open(user_file, "w") as f:
				f.write(data)
