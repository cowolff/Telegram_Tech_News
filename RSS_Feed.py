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
api_key = "key"
chat_id = 1
refresh = 15 # refresh interval in minutes

def send_message(message):
    requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}')

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
    

def determine_send(link, entry):
    keyword_matches = []
    tag_matches = []
    
    if link[2][0] == '' and link[1][0] == '':
        return True

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


if __name__=="__main__":
    started = False
    while True:
        news_links = []
        try:
            news_links = get_config()
        except Exception as e:
            print(e)
        now = datetime.datetime.now()
        if now.hour > 7 and now.hour < 22:
            for link in news_links:
                NewsFeed = feedparser.parse(link[0])
                for entry in NewsFeed.entries:
                    tag_matches = []
                    if entry not in news_content:
                        news_content.append(entry)
                        if started and determine_send(link, entry):
                            print(entry.title)
                            send_message(entry.title + "\n\n" + entry.summary)
                            
            started = True
            print("Checked", now)
        time.sleep(refresh * 60)