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
			userids = wechatpush.get_userids()
			default_urls = WeChat_Config["type"]["News"]["default_urls"]
			userid_fav = WeChat_Config["type"]["News"]["userid_fav"]
			for userid in userids:
				self.news_urls[userid] = []
				self.userid_urls[userid] = default_urls
				if userid in userid_fav:
					self.userid_urls[userid] = userid_fav[userid]


		self.session = HTMLSession()

		self.wechatpush = wechatpush
		

		self.crawl_news() # add those old news to self.news_urls

	def has_numbers(self, inputString):
		return any(char.isdigit() for char in inputString)

	def if_file_exists(self, file_name, userid):
		if os.path.exists(file_name):
			
			# read f from file
			f = open(file_name)
			data = json.load(f)

			for each in data["NewsInfo"]:
				self.news_urls[userid].append(each['url'])
			# self.news_urls[userid] = data["urls"]
			f.close()
			return True

		else:
			# create a new blank file
			self.news_urls[userid] = []
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
		for userid in self.userid_urls:

			user_file = os.path.join(NEWS_DATA_DIR, userid + ".json")
			file_exists = self.if_file_exists(user_file, userid)

			NewsInfo = []

			for each in self.userid_urls[userid]:
				res = self.session.get(each)
				absolute_links = res.html.absolute_links

				for link in absolute_links:

					if "https://zendaily.xyz/p/" in link and "comments" not in link:

						if link not in self.news_urls[userid]:
							print("Found new zendaily post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

					elif "https://www.theblockbeats.info" in link and "search" not in link and self.has_numbers(link):
						
						if link not in self.news_urls[userid]:
							print("Found new blockbeats post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

					elif "https://en.bitpush.news/articles" in link and "tag" not in link:

						if link not in self.news_urls[userid]:
							print("Found new bitpush post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

					elif "https://nftevening.com" in link and "respond" not in link:

						if link not in self.news_urls[userid]:
							print("Found new nftevening post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

					elif "https://newsbtc.com/news/" in link and '-' in link:

						if link not in self.news_urls[userid]:
							print("Found new newsbtc post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

					elif 'articledetails' in link or 'sqarticledetails' in link:
						
						if link not in self.news_urls[userid]:
							print("Found new panewslab post")
							NewsInfo.append({
								"url": link,
								"date": DATE
							})

			links = []
			if file_exists:
				for each in NewsInfo:
					links.append(each["url"])
				userlinks[userid] = links
			else:
				
				data = {
					"NewsInfo": NewsInfo
				}

				data = json.dumps(data)

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

			# Update News_collection.json file
			NewsInfo = []
			for each in self.news_urls[userid]:
				NewsInfo.append({
					"url": each,
					"date": DATE 
				})
			data = {
				"NewsInfo": NewsInfo
			}
			data = json.dumps(data)
			user_file = os.path.join(NEWS_DATA_DIR, userid + ".json")
			with open(user_file, "w") as f:
				f.write(data)
