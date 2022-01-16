import feedparser
import time
import datetime
import re
import logging
import requests
from Database import Data
from Update import get_update, send_message, send_message_to_chats
import random
import threading
from datetime import datetime, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


api_key = ""
refresh = 30 # refresh interval in minutes

def get_config():
    with open("config.txt", "r") as conf:
        news_links = []
        for line in conf:
            config = line.split(" ")
            link = config[config.index("Link:") + 1]
            tags = re.split('[()]', line)[1].split(", ")
            keywords = re.split('[()]', line)[3].split(", ")
            news_links.append((link, tags, keywords))
        return news_links

def rss_process(api_key):
    data = Data()
    chat_ids = data.get_chats()
    print("Gathering RSS Feeds")
    thread = threading.Thread(target=process_news, daemon=True, args=(api_key,))
    thread.start()
    while True:
        data = Data()
        chat_ids = data.get_chats()
        minute = random.randrange(0, 59)
        second = random.randrange(0, 59)
        x=datetime.now()
        y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=second, microsecond=0) + timedelta(minutes=refresh)
        delta_t=y-x
        secs=delta_t.total_seconds()
        time.sleep(secs)
        if x.hour < 23 or x.hour > 8:
            print("Gathering RSS Feeds")
            thread = threading.Thread(target=process_news, daemon=True, args=(api_key,))
            thread.start()

def determine_send(link, entry):
    keyword_matches = []
    tag_matches = []
    
    #if link[2][0] == '' and link[1][0] == '':
    #    return True
    return False
    if hasattr(entry, 'tags') and link[1][0] != '':
        tag_matches = [i for i in link[1] if i in [x.term for x in entry.tags]]
    if link[2][0] != '':
        keyword_matches = [i for i in link[2] if i in str(entry.title)]

    if len(keyword_matches) > 0 and link[1][0] == '':
        return True

    if len(tag_matches) > 0 and link[2][0] == '':
        return True

    if link[1][0] != '' and len(tag_matches) > 0 and link[2][0] != '' and len(keyword_matches) > 0:
        return True

    return False

def process_news(api_key):
    data = Data()
    news_links = data.get_RSS_Feeds()
    print(news_links)
    for link in news_links:
        news_content = data.get_RSS_News(link["link"], link["title"])
        news_content = [x["title"] for x in news_content]
        NewsFeed = feedparser.parse(link["link"])
        for entry in NewsFeed.entries:
            if str(entry.title).replace("'", "") not in news_content:
                try:
                    tags = ' '.join(str(e.term) for e in entry.tags)
                    tags = tags.replace("'", "")
                except:
                    tags = "None"
                print(tags)
                id = data.add_RSS_News(link["link"], str(entry.title).replace("'", ""), tags, time.time(), -1)
                if determine_send(link, entry):
                    print(entry.title)
                    send_message_to_chats(entry.title + "\n\n" + entry.summary + "\n\n" + str(entry.link), data.get_chats(), api_key, id, "RSS")

if __name__=="__main__":
    data = Data()
    while True:
        news_links = []
        try:
            news_links = get_config()
        except Exception as e:
            print(e)
        now = datetime.datetime.now()
        if now.hour > 7 and now.hour < 22:
            get_update(data, api_key)
            process_news(news_links, data)
            print("Checked", now)
        time.sleep(refresh * 60)
