from Database import Data
import requests
from datetime import datetime, timedelta
import time
from Update import get_update, send_message, send_message_to_chats

def twitter_process():
    while True:
        current_dateTime = datetime.now()
        try:
            data = Data()
            feeds = data.get_twitter_feeds()
            barer = data.get_twitter_api()
            api_key = data.get_api_key()["api_key"]
            for feed in feeds:
                feedId = feed["id"]
                url = f"https://api.twitter.com/2/users/{feedId}/tweets"
                headers = {"Authorization": "Bearer {}".format(barer)}
                params = {"exclude":"replies"}
                response = requests.request("GET", url, headers = headers, params=params).json()
                for tweet in response["data"]:
                    new = data.add_tweet(tweet["id"], feedId, tweet["text"])
                    if new:
                        if determine_send_twitter(tweet["text"], feedId, data):
                            feedName = feed["username"]
                            send_message_to_chats(f"New possibly relevant Tweet from https://twitter.com/{feedName}\n\nContent:\n" + tweet["text"], data.get_chats(), api_key, tweet["id"], "Twitter")
                print(len(response["data"]))
        except Exception as e:
            print(e)
        wait = current_dateTime + timedelta(minutes=10)
        now = datetime.now()
        delta_t = wait - now
        secs = delta_t.total_seconds()
        time.sleep(secs)

def determine_send_twitter(text, feed_id, data: Data):

    keywords = data.get_twitter_keywords(feed_id)
    keywords = [word["word"].lower() for word in keywords]

    text = text.lower()

    if len([key for key in keywords if key == "all"]) > 0:
        return True

    if any(word in text for word in keywords):
        return True
    else:
        return False