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

def rss_process():
    data = Data()
    get_update()
    chat_ids = data.get_chats()
    api_key = data.get_api_key()["api_key"]
    thread = threading.Thread(target=process_news, daemon=True, args=(api_key,))
    thread.start()
    while True:
        data = Data()
        get_update()
        api_key = data.get_api_key()["api_key"]
        chat_ids = data.get_chats()
        minute = random.randrange(0, 59)
        second = random.randrange(0, 59)
        x=datetime.now()
        y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=second, microsecond=0) + timedelta(minutes=refresh)
        delta_t=y-x
        secs=delta_t.total_seconds()
        time.sleep(secs)
        if x.hour < 22 or x.hour > 8:
            thread = threading.Thread(target=process_news, daemon=True, args=(api_key,))
            thread.start()

def determine_send(title, tags, feed_id, data: Data):

    keywords = data.get_rss_keywords(feed_id)
    keywords = [word["word"].lower() for word in keywords]
    feed_tags = data.get_rss_tags(feed_id)
    feed_tags = [tag["tag"].lower() for tag in feed_tags]

    if any(word in title for word in keywords) or len(keywords) == 0:
        pass
    else:
        return False

    if any(tag in tags for tag in feed_tags) or len(tags) == 0:
        pass
    else:
        return False

    return True

def process_news(api_key):
    data = Data()
    news_links = data.get_RSS_Feeds()
    for link in news_links:
        news_content = data.get_RSS_News(link["link"], link["title"])
        news_content = [x["title"] for x in news_content]
        NewsFeed = feedparser.parse(link["link"])
        for entry in NewsFeed.entries:
            title = str(entry.title).replace("'", "")
            if title not in news_content:
                try:
                    tags = ' '.join(str(e.term).lower() for e in entry.tags)
                    tags = tags.replace("'", "")
                except:
                    tags = "None"
                id = data.add_RSS_News(link["link"], title, tags, time.time(), -1)
                if determine_send(title, tags, link["feedId"], data) and api_key != "no_value":
                    print(entry.title)
                    send_message_to_chats(entry.title + "\n\n" + entry.summary + "\n\n" + str(entry.link), data.get_chats(), api_key, id, "RSS")

