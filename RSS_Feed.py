import feedparser
import time
import datetime
import re
import logging
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


started = False
news_content = []
api_key = "1719127362:AAEmDqPFza4SGdW5dF6W2sJC6bxiKAV-ebI"
chat_id = 653734838

def send_message(message):
    requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}')



while True:
    news_links = []
    try:
        with open("config.txt", "r") as conf:
            for line in conf:
                config = line.split(" ")
                link = config[config.index("Link:") + 1]
                tags = re.split('[()]', line)[1].split(", ")
                news_links.append((link, tags))
    except:
        pass
    
    now = datetime.datetime.now()
    if now.hour > 7 and now.hour < 22:
        for target in news_links:
            NewsFeed = feedparser.parse(target[0])
            for entry in NewsFeed.entries:
                tag_matches = []
                if hasattr(entry, 'tags'):
                    tag_matches = [i for i in target[1] if i in [x.term for x in entry.tags]]
                if entry not in news_content:
                    news_content.append(entry)
                    if (len(tag_matches) > 0 or target[1][0] == ''):
                        print("TEST")
                        send_message(entry.title + "\n\n" + entry.summary)
                        break
        started = True
        print("Checked", len(news_content))
        time.sleep(10)
